import matplotlib.pyplot as plt

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
