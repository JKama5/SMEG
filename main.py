import numpy as np
from calculations.load_save import load_coil_mesh, load_loops
from calculations.magnetic_field_calculations import create_mesh_conductor, calculate_magnetic_field_at_center
from calculations.plot_results import plot_magnetic_field_vs_current, plot_3d_model

# Load coil mesh and loops
coilmesh_data = load_coil_mesh()
loops = load_loops()

# Create MeshConductor
coil = create_mesh_conductor(coilmesh_data['vertices'], coilmesh_data['faces'])

# Set up target points
center = np.array([0, 0, 0])
sidelength = 0.2  # 0.2 meter
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

# This is used for the plot_magnetic_field_vs_current method
# Calculate magnetic field at the new center point for currents from 0mA to 100mA
currents_mA = np.linspace(0, 100, 101)  # 0mA to 100mA in 1mA steps
B_fields_at_center = calculate_magnetic_field_at_center(loops, target_points, currents_mA)


current_mA = 100  # 1 mA
current_A = current_mA * 1e-3  # Convert mA to A


from bfieldtools.line_conductor import LineConductor
line_conductor = LineConductor(loops=loops)
B_fields_at_targets = line_conductor.magnetic_field(target_points) * current_A

# Plot the 3D model
plot_3d_model(coilmesh_data['vertices'], coilmesh_data['faces'], loops, target_points, B_fields_at_targets)


# Plot the results
plot_magnetic_field_vs_current(currents_mA, B_fields_at_center)

