import matplotlib.pyplot as plt
import pyvista as pv
import numpy as np

def plot_magnetic_field_vs_current(currents_mA, B_fields_at_center):
    """Plot the magnetic field at the center point as a function of current."""
    plt.figure(figsize=(10, 6))
    plt.plot(currents_mA, B_fields_at_center, label='Magnetic Field at Center Point')
    plt.xlabel('Current (mA)')
    plt.ylabel('Magnetic Field (T)')
    plt.title('Magnetic Field at Center Point vs. Current')
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

    # Add target points
    plotter.add_points(target_points, color='red', point_size=5)

    # Create arrows to represent the magnetic field at each target point
    for point, vector in zip(target_points, B_fields_at_targets):
        if vector is not None and np.linalg.norm(vector) > 0:  # Only create arrows for non-zero vectors
            arrow = pv.Arrow(start=point, direction=vector, scale=0.05)
            plotter.add_mesh(arrow, color='magenta')

    plotter.show()