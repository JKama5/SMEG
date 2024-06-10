import numpy as np
from bfieldtools.mesh_conductor import MeshConductor
from bfieldtools.line_conductor import LineConductor

def create_mesh_conductor(vertices, faces):
    """Create a MeshConductor object."""
    return MeshConductor(
        verts=vertices,
        tris=faces,
        fix_normals=True,
        basis_name="suh",
        N_suh=400,
    )

def calculate_magnetic_field_at_center(loops, target_points, currents_mA):
    """Calculate the magnetic field at the center point for a range of currents."""
    line_conductor = LineConductor(loops=loops)
    center_point = np.array([0, 0, 0])
    B_fields_at_center = []

    for current_mA in currents_mA:
        current_A = current_mA * 1e-3  # Convert mA to A
        B_field_unit_current = line_conductor.magnetic_field(np.array([center_point]))
        B_field_at_center = B_field_unit_current * current_A
        B_fields_at_center.append(np.linalg.norm(B_field_at_center[0]))  # Store the magnitude of the magnetic field

    return B_fields_at_center
