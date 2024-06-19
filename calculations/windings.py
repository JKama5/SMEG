import numpy as np
import trimesh
import pickle
from bfieldtools.mesh_conductor import MeshConductor
from bfieldtools.coil_optimize import optimize_streamfunctions
from bfieldtools.contour import scalar_contour
import pkg_resources
import mosek

LOOPS = None

def generate_windings(new_radius_scale=(0.75)/2, new_height_scale=(0.5)/2, n_contours=7):
    # Load example coil mesh
    coilmesh = trimesh.load(
        file_obj=pkg_resources.resource_filename(
            "bfieldtools", "example_meshes/open_cylinder.stl"
        ),
        process=True,
    )

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

    # Set up target points
    center = np.array([0, 0, 0])
    sidelength = 0.4  # 0.2 meter
    n = 8
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
    undesired_field[:, 1] =  1  # Example non-uniform field in y-direction
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
        
        with open('coilmesh_Y.pkl', 'wb') as f:
            pickle.dump({'vertices': coilmesh1.vertices, 'faces': coilmesh1.faces}, f)

        with open('loops_Y.pkl', 'wb') as f:
            pickle.dump(loops, f)

        return True
    else:
        return False



if __name__ == "__main__":
    success = generate_windings()
    if success:
        print("Windings generated and saved successfully.")
    else:
        print("Failed to generate windings.")