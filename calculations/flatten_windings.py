import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt

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

def flatten_loops(loops):
    """Flatten the coil loops from a cylinder to a plane."""
    flattened_loops = []
    for loop in loops:
        points = loop.copy()

        # Convert cylindrical coordinates to flat plane
        r = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
        theta = np.arctan2(points[:, 1], points[:, 0])

        # Create new points with flattened coordinates for the PCB
        flattened_points = np.zeros_like(points)
        flattened_points[:, 0] = theta * r  # X-coordinate: theta * r (unwrapped angle)
        flattened_points[:, 1] = points[:, 2]  # Y-coordinate: original Z-coordinate
        flattened_points[:, 2] = 0  # Z-coordinate flattened to 0

        flattened_loops.append(flattened_points)
    return flattened_loops

def plot_loops_2d(loops, colors, plotter):
    for i, loop in enumerate(loops):
        color = colors[i]
        loop[:, 2] = 0  # Set Z-coordinate to 0 for 2D plotting
        loop_polydata = pv.PolyData(loop)
        plotter.add_mesh(loop_polydata, color=color, line_width=2)
    
    # Set camera to orthographic projection and lock position
    plotter.camera.SetParallelProjection(True)
    plotter.camera_position = 'xy'
    plotter.view_xy()
    plotter.show_axes()
    plotter.disable()
    plotter.show(interactive_update=False)

