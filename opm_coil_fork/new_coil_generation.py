import numpy as np
import scipy
import trimesh
import pyvista as pv
import mosek
import math
import matplotlib.pyplot as plt
from bfieldtools.mesh_conductor import MeshConductor
from bfieldtools.coil_optimize import optimize_streamfunctions
from bfieldtools.contour import scalar_contour
from bfieldtools.line_conductor import LineConductor
from metrics import homogeneity, efficiency, error
from line_drawer import LineDrawer, get_shifted_line
from file_io import get_loop_colors, export_to_kicad, _check_bounds
from make_pcb import join_loops_at_cuts
import pickle
import pkg_resources
from flatten_windings import flatten_loops, plot_loops_2d, determine_color_auto

"""
This script is written to generate windings specific for the Single Layer MSR
The maximum field in the room is around 25nT so the coil is designed to null
only nT fields in the x, y, and z direction. The coil is cylidnrical and then
transformed to be a planar coil for PCB fabrication.

"""


def generate_windings(coil_type, new_diamater=0.96/2, new_height_scale=0.50/2, n_contours=3):
    """
    Generate windings for the coil.

    Parameters
    ----------
    new_radius_scale : float, optional
        The multiplier for the mesh's radius, by default 0.96/2
    new_height_scale : float, optional
        The multiplier for the mesh's height, by default 0.50/2
    n_contours : int, optional
        How many contours the windings should take, by default 3
    coil_type : str, optional
        The coil type, expects either 'X','Y','Z' based on the sheilded rooms reference frame, by default 'Z'

    Returns
    -------
    tuple
        A tuple containing the vertices, faces, stream functions, loops, target points, and target field.
    """
    
    # Load example coil mesh
    coilmesh = trimesh.load(
        file_obj=pkg_resources.resource_filename(
            "bfieldtools", "example_meshes/open_cylinder.stl"
        ),
        process=True,
    )
    ### Adjust the coil mesh for the new radius and height
    ### This is the decided scaling for each of the meshes
    if coil_type == 'X':
        n_contours = 3
        new_diameter = 1.0

    if coil_type == 'Y': 
        n_contours = 11
        new_diameter= 0.98
    if coil_type == 'Z':
        n_contours = 3 
        new_diameter = 0.96
    coilmesh1 = coilmesh.copy()

    # Adjust the coil mesh vertices for the new radius and height
    coilmesh1.vertices[:, :2] *= new_diameter  # Scale x and y coordinates for radius
    coilmesh1.vertices[:, 2] *= new_height_scale  # Scale z coordinate for height


    # Create MeshConductor
    coil = MeshConductor(
        verts=coilmesh1.vertices,
        tris=coilmesh1.faces,
        fix_normals=True,
        basis_name="suh",
        N_suh=400,
    )

    # Define target points
    center = np.array([0, 0, 0])
    sidelength = 0.4  # 0.4 meter
    n = 9
    xx = np.linspace(-sidelength / 2, sidelength / 2, n)
    yy = np.linspace(-sidelength / 2, sidelength / 2, n)
    zz = np.linspace(-sidelength / 2, sidelength / 2, n)
    X, Y, Z = np.meshgrid(xx, yy, zz, indexing="ij")

    x = X.ravel()
    y = Y.ravel()
    z = Z.ravel()

    target_points = np.array([x, y, z]).T
    target_points = target_points[np.linalg.norm(target_points, axis=1) < sidelength / 2] + center

    # Define the undesired magnetic field
    undesired_field = np.zeros(target_points.shape)
    if coil_type == 'X': undesired_field[:, 1] = 25e-9      # Example non-uniform field in x-direction (rooms reference frame)
    elif coil_type == 'Y': undesired_field[:, 2] = 25e-9    # Example non-uniform field in y-direction (rooms reference frame)
    elif coil_type == 'Z': undesired_field[:, 0] = 25e-9    # Example non-uniform field in z-direction (rooms reference frame)
    else: raise ValueError("Invalid coil type. Must be 'X', 'Y', or 'Z'.")
    target_field = -undesired_field

    # Create bfield specifications
    target_spec = {
        "coupling": coil.B_coupling(target_points),
        "abs_error": 0.01,
        "target": target_field,
    }

    try:
        coil.s, prob = optimize_streamfunctions(
            coil,
            [target_spec],
            objective="minimum_inductive_energy",
            solver="MOSEK",
            solver_opts={"mosek_params": {mosek.iparam.num_threads: 8}},
        )
    except Exception as e:
        print(f"Optimization failed: {e}")
        coil.s = None

    if coil.s is not None:
        loops = scalar_contour(coil.mesh, coil.s.vert, N_contours=n_contours)

        #Save the data for the coil through Pickle to make use of faster code testing and debugging
        if coil_type == 'X':
            with open(f'coilmesh_{coil_type}.pkl', 'wb') as f:
                pickle.dump({'vertices': coilmesh1.vertices, 'faces': coilmesh1.faces}, f)

            with open(f'loops_{coil_type}.pkl', 'wb') as f:
                pickle.dump(loops, f)

            with open(f'target_points_{coil_type}.pkl', 'wb') as f:
                pickle.dump(target_points, f)

        if coil_type == 'Z':
            with open(f'final_coilmesh_{coil_type}.pkl', 'wb') as f:
                pickle.dump({'vertices': coilmesh1.vertices, 'faces': coilmesh1.faces}, f)

            with open(f'final_loops_{coil_type}.pkl', 'wb') as f:
                pickle.dump(loops, f)

            with open(f'final_target_points_{coil_type}.pkl', 'wb') as f:
                pickle.dump(target_points, f)

        return coilmesh1.vertices, coilmesh1.faces, coil.s, loops, target_points, target_field, new_diameter
    else:
        return None, None, None, None, None, None, None


class CylindricalCoil:
    """Cylindrical coil.

    Parameters
    ----------
    coil_type : str, optional
        The coil type, expects either 'X','Y','Z' based on the sheilded rooms reference frame, by default 'X'.

    Attributes
    ----------
    trace_width : float
        The trace width of the coil in mm.
    cu_oz : float
        The copper ounces per square feet.
    loops_ : loop
        The discretized current loop.
    inductance : float
        The coil self-inductance in uH.
    length : float
        The total length of the coil in m.
    resistance : float
        The resistance of the coil in ohms.
    """

    def __init__(self, coil_type):
        """
        Initialize the CylindricalCoil class.

        Parameters
        ----------
        new_diameter : float
            The multiplier for the mesh's radius.
        new_height_scale : float
            The multiplier for the mesh's height.
        n_contours : int, optional
            How many contours the windings should take, by default 3 (Y is 2).
        coil_type : str, optional
            The coil type, expects either 'X','Y','Z' based on the sheilded rooms reference frame, by default 'X'.
        """

        vertices, faces, s, loops, target_points, target_field, diameter = generate_windings(coil_type)

        self.vertices = vertices
        self.faces = faces
        self.s = s
        self.loops = loops
        self.target_points = target_points
        self.target_field = target_field
        self.trace_width = 5     # in mm
        self.cu_oz = 2           # oz per ft^2
        self.FCu = list()
        self.BCu = list()
        self.line_conductor_ = LineConductor(loops=loops)
        self.flatloops = flatten_loops(loops, coil_type)
        self.coil_type = coil_type
        self.radius = diameter/2
        self.circum = math.pi*2*self.radius *1000
        self.color = determine_color_auto(self.loops, (0, 0, 0))

        # Scale the loops
        for i, loop in enumerate(self.flatloops):
            self.flatloops[i][:, 0] = loop[:, 0] * 1000
            self.flatloops[i][:, 1] = loop[:, 1] * 1000

    def predict(self, target_points):
        """Predict the field.

        Parameters
        ----------
        target_points : array, (n_points, 3)
            Plot the field at the target points.

        Returns
        -------
        B_predicted : array, (n_points, 3)
            The predicted field at the target points.
        """
        B_predicted = self.line_conductor_.magnetic_field(target_points) * 1e-3
        return B_predicted @ self.s

    def evaluate(self, target_points, target_field,
                 metrics='all', target_type='dc'):
        """Evaluate the coil.
        
        Parameters
        ----------
        target_points : array, (n_points, 3)
            Plot the field at the target points.
        metrics : str or list, optional
            The metrics to evaluate, by default 'all'.
        target_type : str, optional
            The target type, by default 'dc'.

        Returns
        -------
        dict
            A dictionary containing the evaluation scores.
        """
        if metrics == 'all':
            metrics = ['efficiency', 'error', 'homog', 'inductance',
                       'resistance', 'length', 'target_radius']

        scores = dict()
        for metric in metrics:
            if metric == 'efficiency':
                ef, _ = efficiency(self.line_conductor_, target_points,
                                   target_type)
                scores['efficiency (nT/mA)'] = ef
            elif metric == 'error':
                err = error(self, target_field, target_points, target_type)
                scores['error'] = err
            elif metric == 'homog':
                hmg = homogeneity(self, target_field, target_points, target_type)
                scores['homogeneity (%)'] = hmg
            elif metric == 'inductance':
                scores['inductance (uH)'] = self.inductance
            elif metric == 'resistance':
                scores['resistance (ohm)'] = self.resistance
            elif metric == 'length':
                scores['length (m)'] = self.length
            elif metric == 'target_radius':
                scores['target radius (cm)'] = target_points[:, 2].max() * 100
        return scores

    @property
    def length(self):
        """The length of the coil."""
        return self.line_conductor_.length

    @property
    def resistance(self):
        """The coil resistance."""
        # this formulation for PCB resistance matches the internet calculators
        rho = 1.72e-8                       # ohm-m at 25C
        thickness = self.cu_oz * 35e-6      # (1 oz cu == 35 um thick)
        width = self.trace_width * 1e-3     # m

        resistance = rho * self.length / (width * thickness)
        return resistance

    @property
    def inductance(self):
        """The coil self-inductance"""
        return self.s.coil_inductance(Nloops=len(self.loops)) * 1e6


    def make_cuts(self):
        """Make cuts to join loops."""
        import matplotlib.pyplot as plt

        loops = list()
        for loop in self.flatloops:
            # Check if the loop is closed by comparing the first and last points
            if not np.allclose(loop[0], loop[-1]):
                loop = np.vstack([loop, loop[0]])  # make closed loop
            loops.append((np.array(loop)))


        colors = determine_color_auto(self.loops, (0,0,0))

        fig = plt.figure()
        for color, loop in zip(colors, loops):
            loop_arr = np.array(loop)
            #If the loops are in a cylinder (only on Y coil) they need to be correctly wrapped
            if self.coil_type == 'Y':
                # Sort based on the first column (x coordinate)
                sorted_points = loop_arr[loop_arr[:, 0].argsort()]
                loop_arr = sorted_points
            plt.plot(loop_arr[:, 0], loop_arr[:, 1], color=color)
        plt.show()

        # ld = LineDrawer(fig)
        # line_cuts, line_cuts_shifted = ld.get_line_cuts()

        # fig, axes = plt.subplots(2, 1, sharex=True, sharey=True, figsize=(8, 8))
        # for line_cut, line_cut_shifted in zip(line_cuts, line_cuts_shifted):
        #     continuous_loop, reverse_paths, _, _, _, direction = join_loops_at_cuts(
        #         loops, line_cut, line_cut_shifted, colors)
        #     self.FCu.append(continuous_loop)
        #     self.BCu.append(reverse_paths)

        #     color = 'r' if direction == 'cc' else 'b'
        #     axes[0].plot(continuous_loop[:, 0], continuous_loop[:, 1], f'{color}-', alpha=0.6)
        #     axes[1].plot(reverse_paths[:, 0], reverse_paths[:, 1], 'g', zorder=0, linewidth=3, alpha=0.6)
        # plt.show()

    def assign_front_back(self):
        """Assign front and back loops."""
        color = determine_color_auto(self.loops, (0, 0, 0))
        
        for i, _ in enumerate(self.flatloops):
            if color[i] == 'r':
                self.FCu.append(self.flatloops[i])
            else:
                self.BCu.append(self.flatloops[i])


    def save(self, pcb_fname, kicad_header_fname, origin,
             bounds=None, bounds_wholeloop=True, side = None, bound = 0):
        """Save the files to be loaded in KICAD.

        Parameters
        ----------
        pdb_fname : str
            The file name of the KICAD pcb file.
        kicad_header_fname : str
            The file name of the KICAD header.
        bounds : tuple of (min_x, max_x, min_y, max_y)
            Save only loops within the bounds expressed in mm.
        origin : tuple of (x, y)
            The origin in mm.
        """
        # FCu_truncated = list()
        # BCu_truncated = list()
        # for FCu_loop, BCu_loop in zip(self.FCu, self.BCu):
        #     if _check_bounds(FCu_loop, bounds) or (bounds_wholeloop is False):
        #         FCu_truncated.append(FCu_loop)
        #         BCu_truncated.append(BCu_loop)
        
        export_to_kicad(pcb_fname=pcb_fname,
                        kicad_header_fname=kicad_header_fname,
                        origin=origin,
                        loops={'F.Cu': self.FCu, 'B.Cu': self.BCu},
                        net=1, scaling=1, trace_width=self.trace_width,
                        bounds=bounds, bounds_wholeloop=bounds_wholeloop,
                        side = side, bound = bound)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    coil_type = 'Y'
    pcb_name = f'final_coil_{coil_type}.kicad_pcb' 
    kicad_header_fname = 'kicad_header.txt'
    bounds = (-2300,2300,-2300,2300)
    
    # Create an instance of CylindricalCoil
    coil = CylindricalCoil(coil_type=coil_type)
    origin = (-(coil.circum / 2.0 ),0)
    length = coil.length
    print(f"Length: {length}")
    coil.assign_front_back()
    coil.save(pcb_name, kicad_header_fname, bounds=bounds, origin=origin, side = "left", bound = 2000)
    print(f"Resiatance: {coil.resistance}")
    
    

