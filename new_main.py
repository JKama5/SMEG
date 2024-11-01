import numpy as np
from calculations.load_save import load_coil_mesh, load_loops, load_target_points
from calculations.magnetic_field_calculations import create_mesh_conductor, calculate_magnetic_field_at_points
from calculations.plot_results import plot_magnetic_field_vs_current, plot_3d_model
import pyvista as pv
from calculations.flatten_windings import flatten_loops, plot_loops_2d, determine_color_auto

#from opm_coil_fork.biplanar_coil import BiplanarCoil

# Load coil mesh and loops
coilmesh_data = load_coil_mesh('coilmesh_Z.pkl')
loops = load_loops('loops_Z.pkl')
target_points = load_target_points('target_points_Z.pkl')
origin = np.zeros(3) 
currents_mA = np.linspace(0, 100, 101)  # 0mA to 100mA in 1mA steps
current_mA = 10  # 10 mA
current_A = current_mA * 1e-3  # Convert mA to A

# Bfield simulation
from bfieldtools.line_conductor import LineConductor

points = np.array([[0.15,0,.10],[0.10,0,.10],[0.05,0,.10],[0,0,.10],[-0.05,0,.10],[-0.10,0,.10],[-0.15,0,.10],
                  [0.15,0,.05],[0.10,0,.05],[0.05,0,.05],[0,0,.05],[-0.05,0,.05],[-0.10,0,.05],[-0.15,0,.05],
                  [0.15,0,0],[0.10,0,0],[0.05,0,0],[0,0,0],[-0.05,0,0],[-0.1,0,0],[-0.15,0,0],
                  [0.15,0,-.05],[0.10,0,-.05],[0.05,0,-.05],[0,0,-.05],[-0.05,0,-.05],[-0.10,0,-.05],[-0.15,0,-.05],
                  [0.15,0,-.10],[0.10,0,-.10],[0.05,0,-.10],[0,0,-0.1],[-0.05,0,-.10],[-0.10,0,-.10],[-0.15,0,-.10]])

line_conductor = LineConductor(loops=loops)
B_fields_at_targets = line_conductor.magnetic_field(target_points) * current_A
#B_fields_at_targets = line_conductor.magnetic_field(points) * current_A

# Plot the 3D model of the coil, windings, and magnetic field
#eff = record_magnetic_field_at_100mA(loops,points)
#print(eff[:,1]*10e6)
B_fields_at_center = calculate_magnetic_field_at_points(loops, origin, currents_mA)
plot_magnetic_field_vs_current(currents_mA, B_fields_at_center)

B_fields_at_targets = line_conductor.magnetic_field(target_points) * current_A
plot_3d_model(coilmesh_data['vertices'], coilmesh_data['faces'], loops, target_points, B_fields_at_targets)


# Plot the 2D model of the coil windings for PCB fabrication
flattened_loops = flatten_loops(loops, 'Z')
colors = determine_color_auto(loops, origin)
flat = plot_loops_2d(flattened_loops, colors, plotter=pv.Plotter())

# Create a "biplanar coil" that will be cut

#flat_coil = BiplanarCoil()


