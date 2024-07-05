import numpy as np
import trimesh
import pickle
from bfieldtools.mesh_conductor import MeshConductor
from bfieldtools.coil_optimize import optimize_streamfunctions
from bfieldtools.contour import scalar_contour
import pkg_resources
import mosek


def generate_windings(new_diameter=750, new_height_scale=500/2, n_contours=50, coil_type='Z'):
            # COIL TYPE IS FOR THE ROOMS PERSPECTIVE
    # Load example coil mesh
    coilmesh = trimesh.load(
        file_obj=pkg_resources.resource_filename(
            "bfieldtools", "example_meshes/open_cylinder.stl"
        ),
        process=True,
    )

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
    sidelength = 100 # mm
    n = 4
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
    if coil_type == 'X': undesired_field[:, 1] = 25e-9      # Example non-uniform field in x-direction
    elif coil_type == 'Y': undesired_field[:, 2] = 25e-9    # Example non-uniform field in y-direction
    elif coil_type == 'Z': undesired_field[:, 0] = 25e-9    # Example non-uniform field in z-direction
    else: raise ValueError("Invalid coil type. Must be 'X', 'Y', or 'Z'.")
    target_field = -undesired_field

    # Create bfield specifications
    target_spec = {
        "coupling": coil.B_coupling(target_points),
        "abs_error": 0.05,
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