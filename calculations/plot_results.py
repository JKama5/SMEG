import matplotlib.pyplot as plt
import pyvista as pv
import numpy as np

def plot_magnetic_field_vs_current(currents_mA, B_fields_at_points):
    """Plot the magnetic field at each target point as a function of current."""
    num_points = B_fields_at_points.shape[1]

    for idx in range(num_points):
        B_fields_at_point = B_fields_at_points[:, idx, :]
        B_magnitudes = np.linalg.norm(B_fields_at_point, axis=1)
        plt.figure(figsize=(10, 6))
        plt.plot(currents_mA, B_magnitudes, label=f'Magnetic Field at Point {idx}')
        plt.xlabel('Current (mA)')
        plt.ylabel('Magnetic Field (T)')
        plt.title(f'Magnetic Field at Point {idx} vs. Current')
        plt.legend()
        plt.grid(True)
        plt.show()

        
def plot_3d_model(vertices, faces, loops, target_points, B_fields_at_targets):
    """Plot a 3D model of the coil, windings, and magnetic field."""
    plotter = pv.Plotter()
    plotter.set_background("white")

    # Create a PolyData object for the coil mesh
    meshviz_coil = pv.PolyData(vertices, np.hstack((np.repeat(3, len(faces))[:, None], faces)))
    plotter.add_mesh(meshviz_coil, opacity=0.1, color='blue')

    # Add the coil windings (current loops)
    for loop in loops:
        loop_polydata = pv.PolyData(loop)
        plotter.add_mesh(loop_polydata, color='orange', line_width=2)
        print(loop_polydata)
        print("----------------------------")

    # Add target points
    plotter.add_points(target_points, color='red', point_size=5)

    # Create arrows to represent the magnetic field at each target point
    for point, vector in zip(target_points, B_fields_at_targets):
        if vector is not None and np.linalg.norm(vector) > 0:  # Only create arrows for non-zero vectors
            arrow = pv.Arrow(start=point, direction=vector, scale=0.05)
            plotter.add_mesh(arrow, color='magenta')

    # Add 3D axes
    plotter.add_axes()

    plotter.show()