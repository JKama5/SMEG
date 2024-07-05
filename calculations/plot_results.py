import matplotlib.pyplot as plt
import pyvista as pv
import numpy as np

def plot_magnetic_field_vs_current(currents_mA, B_fields_at_points):
    """Plot the magnetic field at each target point as a function of current."""
    num_points = B_fields_at_points.shape[1]

    for idx in range(num_points):
        B_fields_at_point = B_fields_at_points[:, idx, :]
        B_magnitudes = np.linalg.norm(B_fields_at_point, axis=1)
        
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(currents_mA, B_magnitudes * 1e9, label=f'Magnetic Field at Point {idx}')
        plt.xlabel('Current (mA)')
        plt.ylabel('Magnetic Field (nT)')
        plt.title(f'Magnetic Field at Point {idx} vs. Current')
        plt.legend()
        plt.grid(True)
        plt.show()





def determine_color_auto(current_loops, origin):
    """Determine the color of each loop automatically based on the direction."""
    colors = []
    palette = ["r", "b"]
    for loop in current_loops:
        # Compute each loop segment
        segments = np.vstack((loop[1:, :] - loop[:-1, :], loop[0, :] - loop[-1, :]))

        # Find mean normal vector following right-hand rule, in loop center
        centre_normal = np.mean(np.cross(segments, loop), axis=0)
        centre_normal /= np.linalg.norm(centre_normal, axis=-1)

        # Check if normal "points in" or "out" (towards or away from origin)
        origin_vector = np.mean(loop, axis=0) - origin

        colors.append(palette[int((np.sign(centre_normal @ origin_vector) + 1) / 2)])
    return colors

def plot_3d_model(vertices, faces, loops, target_points, B_fields_at_targets, colors=None, figure=None):
    """Plot a 3D model of the coil, windings, and magnetic field with directionality and color."""
    plotter = pv.Plotter() if figure is None else figure
    plotter.set_background("white")

    # Create a PolyData object for the coil mesh
    meshviz_coil = pv.PolyData(vertices, np.hstack((np.repeat(3, len(faces))[:, None], faces)))
    plotter.add_mesh(meshviz_coil, opacity=0.1, color='blue')

    if colors is None:
        origin = np.zeros(3)  # Assuming origin at (0, 0, 0) for simplicity
        colors = determine_color_auto(loops, origin)

    # Add the coil windings (current loops) with directionality and color
    for i, loop in enumerate(loops):
        color = colors[i]
        loop_polydata = pv.PolyData(loop)
        plotter.add_mesh(loop_polydata, color=color, line_width=2)


    # Add target points
    plotter.add_points(target_points, color='red', point_size=5)

    # # Create arrows to represent the magnetic field at each target point
    for point, vector in zip(target_points, B_fields_at_targets):
        if vector is not None and np.linalg.norm(vector) > 0:  # Only create arrows for non-zero vectors
            arrow = pv.Arrow(start=point, direction=vector, scale=10)
            plotter.add_mesh(arrow, color='magenta')


    # Add 3D axes
    plotter.add_axes()
    plotter.show_bounds(grid='front', location='outer', all_edges=True)

    plotter.show()






# def plot_3d_model(vertices, faces, loops, target_points, B_fields_at_targets):
#     """Plot a 3D model of the coil, windings, and magnetic field."""
#     plotter = pv.Plotter()
#     plotter.set_background("white")

#     # Create a PolyData object for the coil mesh
#     meshviz_coil = pv.PolyData(vertices, np.hstack((np.repeat(3, len(faces))[:, None], faces)))
#     plotter.add_mesh(meshviz_coil, opacity=0.1, color='blue')

#     # Add the coil windings (current loops)
#     for loop in loops:
#         loop_polydata = pv.PolyData(loop)
#         #plotter.add_mesh(loop_polydata, color='orange', line_width=2)
#         #print(loop_polydata)
#         #print("----------------------------")

#     plot_3d_current_loops(loops, colors="auto", figure=plotter, tube_radius=0.005)

#     # Add target points
#     plotter.add_points(target_points, color='red', point_size=5)

#     # Create arrows to represent the magnetic field at each target point
#     for point, vector in zip(target_points, B_fields_at_targets):
#         if vector is not None and np.linalg.norm(vector) > 0:  # Only create arrows for non-zero vectors
#             arrow = pv.Arrow(start=point, direction=vector, scale=0.05)
#             plotter.add_mesh(arrow, color='magenta')

#     # Add 3D axes
#     plotter.add_axes()

#     plotter.show()

