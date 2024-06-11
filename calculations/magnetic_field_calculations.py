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

def calculate_magnetic_field_at_points(loops, points, currents_mA):
    """Calculate the magnetic field at given points for a range of currents."""
    line_conductor = LineConductor(loops=loops)
    B_fields_at_points = []

    for current_mA in currents_mA:
        current_A = current_mA * 1e-3  # Convert mA to A
        B_field_unit_current = line_conductor.magnetic_field(points)
        B_field_at_points = B_field_unit_current * current_A
        B_fields_at_points.append(B_field_at_points)

    return np.array(B_fields_at_points)
