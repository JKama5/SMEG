import ezdxf
import numpy as np
import pyvista as pv
from load_save import load_coil_mesh, load_loops

def save_loops_as_dxf(looppolydata, filename):
    # KiCad accepts DXF
    # Create a new DXF document
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()
    
    # Extract the individual loops and flatten them
    for loop in looppolydata:
        points = loop.points

        # Convert cylindrical coordinates to flat plane
        r = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
        theta = np.arctan2(points[:, 1], points[:, 0])

        # Create new points with flattened coordinates for the pcb
        flattened_points = np.zeros_like(points)
        flattened_points[:, 0] = theta * r  # X-coordinate: theta * r (unwrapped angle)
        flattened_points[:, 1] = points[:, 2]  # Y-coordinate: original Z-coordinate
        flattened_points[:, 2] = 0  # Z-coordinate flattened to 0

        # Add each loop as a polyline to the DXF document for KiCad upload
        msp.add_lwpolyline(flattened_points[:, :2], is_closed=True)
    
    # Save the DXF document for KiCad
    doc.saveas(filename)

loops = load_loops()
loop_polydata_array = [pv.PolyData(loop) for loop in loops]
save_loops_as_dxf(loop_polydata_array, 'Flattened_YYY.dxf')

print("DXF file saved successfully.")