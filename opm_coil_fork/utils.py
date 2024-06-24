"""Utils."""
from bfieldtools.line_conductor import LineConductor

def separate_loops(loops, standoff):
    """Separate the loops."""
    current_loops_separate = dict(L=list(), R=list())
    for loop in loops:
        if np.allclose(loop[:, 1], standoff[1]):
            current_loops_separate['L'].append((np.array(loop)))
        else:
            current_loops_separate['R'].append((np.array(loop)))
    line_conductor_separate = {'L': LineConductor(loops=current_loops_separate['L']),
                               'R': LineConductor(loops=current_loops_separate['R'])}
    return line_conductor_separate


def optimize_currents_analytic(f_dc, f_grad, line_conductor_separate, target_points_y,
                               dy):
    """Optimize currents i1 and i2 to produce f_dc and f_grad."""

    # i1 * n1 + i2 * n2 = f_dc
    # i1 * n3 - i2 * n4 = f_grad
    # now solve for i1 and i2

    unit_field_same = (line_conductor_separate['L'].magnetic_field(points=target_points_y) +
                       line_conductor_separate['R'].magnetic_field(points=target_points_y)) * 1e9 * 1e-3
    unit_field_opposite = (line_conductor_separate['L'].magnetic_field(points=target_points_y) -
                           line_conductor_separate['R'].magnetic_field(points=target_points_y)) * 1e9 * 1e-3

    n1 = same_eta_dc = np.mean(unit_field_same[:, 2])
    n3 = same_eta_grad = np.mean(np.diff(unit_field_same[:, 2])) / dy
    n2 = opposite_eta_dc = np.mean(unit_field_opposite[:, 2])
    n4 = opposite_eta_grad = np.mean(np.diff(unit_field_opposite[:, 2])) / dy

    i1 = (f_dc * n4 + f_grad * n2) / (n1 * n4 + n3 * n2)
    i2 = (f_dc * n3 - f_grad * n1) / (n2 * n3 + n4 * n1)

    return i1, i2

def optimize_currents(f_dc, f_grad, line_conductor_separate, target_points_y):
    """Get currents i1 and i2 to produce f_dc and f_grad."""

    def func(x):
        i1, i2 = x[0], x[1]
        field = (line_conductor_separate['L'].magnetic_field(points=target_points_y) * (i1 + i2) +
                 line_conductor_separate['R'].magnetic_field(points=target_points_y) * (i1 - i2)) * 1e9 * 1e-3
        actual_mean_field = (field[0, 2] + field[-1, 2]) / 2
        actual_grad_field = (field[0, 2] - field[-1, 2]) / (target_points_y[0, 1] - target_points_y[-1, 1])
        return (actual_mean_field - f_dc) ** 2 + (actual_grad_field - f_grad) ** 2

    def callback(x):
        print(x)

    res = scipy.optimize.minimize(func, [0, 0], method='COBYLA', callback=callback,
                                  options={'maxiter': 100})
    i1, i2 = res.x
    return i1, i2


"""
target_dc = 20 # nT

for i1 in [0, 0.2]:  # np.arange(0, 1.0, 0.1):
    # for i2 in np.arange(0, 1.2, 0.2):
    field_y = (line_conductor_separate['L'].magnetic_field(points=target_points_y) * (i1 + i2)
               line_conductor_separate['R'].magnetic_field(points=target_points_y) * i1) * 1e9 * 1e-3
    plt.plot(target_points_y[:, 1], field_y[:, 2], label=f'i1={i1}, i2={i2}')
plt.legend()
plt.show()
"""