import numpy as np
import trimesh
import pickle
from bfieldtools.mesh_conductor import MeshConductor
from bfieldtools.coil_optimize import optimize_streamfunctions
from bfieldtools.contour import scalar_contour
import pkg_resources
import mosek

def generate_windings(coil_type, new_radius_scale=0.73/2, new_height_scale=0.50/2, n_contours=3):
    """
    Generate windings for the coil.

    Parameters
    ----------
    new_radius_scale : float, optional
        The multiplier for the mesh's radius, by default 0.73/2
    new_height_scale : float, optional
        The multiplier for the mesh's height, by default 0.40/2
    n_contours : int, optional
        How many contours the windings should take, by default 3
    coil_type : str, optional
        The coil type, expects either 'X','Y','Z' based on the sheilded rooms reference frame, by default 'Y'

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
        new_radius_scale = 1.0

    if coil_type == 'Y': 
        n_contours = 3
        new_radius_scale = 0.98
    if coil_type == 'Z':
        n_contours = 3 
        new_radius_scale = 0.96
    coilmesh1 = coilmesh.copy()

    # Adjust the coil mesh vertices for the new radius and height
    coilmesh1.vertices[:, :2] *= new_radius_scale  # Scale x and y coordinates for radius
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
    sidelength = 0.4  # 0.3 meter
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
            with open('coilmesh_X.pkl', 'wb') as f:
                pickle.dump({'vertices': coilmesh1.vertices, 'faces': coilmesh1.faces}, f)

            with open('loops_X.pkl', 'wb') as f:
                pickle.dump(loops, f)

            with open('target_points_X.pkl', 'wb') as f:
                pickle.dump(target_points, f)

        if coil_type == 'Y':
            with open('coilmesh_Y.pkl', 'wb') as f:
                pickle.dump({'vertices': coilmesh1.vertices, 'faces': coilmesh1.faces}, f)

            with open('loops_Y.pkl', 'wb') as f:
                pickle.dump(loops, f)

            with open('target_points_Y.pkl', 'wb') as f:
                pickle.dump(target_points, f)
        
        if coil_type == 'Z':
            with open('coilmesh_Z.pkl', 'wb') as f:
                pickle.dump({'vertices': coilmesh1.vertices, 'faces': coilmesh1.faces}, f)

            with open('loops_Z.pkl', 'wb') as f:
                pickle.dump(loops, f)

            with open('target_points_Z.pkl', 'wb') as f:
                pickle.dump(target_points, f)

        return True
    else:
        return False

if __name__ == "__main__":
    success = generate_windings(coil_type='Z')
    if success:
        print("Windings generated and saved successfully.")
    else:
        print("Failed to generate windings.")
