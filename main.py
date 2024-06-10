import numpy as np
from calculations.load_save import save_coil_mesh, load_coil_mesh, save_loops, load_loops
from calculations.magnetic_field_calculations import create_mesh_conductor, calculate_magnetic_field_at_center
from calculations.plot_results import plot_magnetic_field_vs_current

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

# Calculate magnetic field at the new center point for currents from 0mA to 100mA
currents_mA = np.linspace(0, 100, 101)  # 0mA to 100mA in 1mA steps
B_fields_at_center = calculate_magnetic_field_at_center(loops, target_points, currents_mA)

# Plot the results
plot_magnetic_field_vs_current(currents_mA, B_fields_at_center)
