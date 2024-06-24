"""Metrics for evaluating coil designs."""

# Authors: Mainak Jas <mjas@mgh.harvard.edu>
#          Padma Sundaram <padma@nmr.mgh.harvard.edu>

import numpy as np

def _percent_error(coil, target_field, target_points, target_type):
    field = coil.B_coupling(target_points) @ coil.s
    ax = {'x': 0, 'y': 1, 'z': 2}[target_type.split('_')[1]]
    return np.abs((field[:, ax] - target_field[:, ax]) / target_field[:, ax])

def homogeneity(coil, target_field, target_points, target_type,
                allowed_error=0.05):
    """Compute homogeneity percentage with discretized current loops."""
    err = _percent_error(coil, target_field, target_points, target_type)
    count = np.sum(err <= allowed_error)
    return count / target_field.shape[0] * 100

def efficiency(current_loops, target_points, target_type):
    """Compute efficiency with discretized current loops."""
    ax = {'x': 0, 'y': 1, 'z': 2}[target_type.split('_')[1]]
    
    if 'dc' in target_type:
        field = current_loops.magnetic_field(points=target_points)
        # print(field * 1e-3 * 1e9)
        efficiency = np.mean(field * 1e-3 * 1e9, axis=0)[ax]
        unit = 'nT / mA'
    # elif 'grad' in target_type:
    #     field = current_loops.magnetic_field(points=target_points_z)
    #     dB = (field[-1, ax] - field[0, ax]) * 1e-3 * 1e9 # nT
    #     dz = target_points_z[-1, 2] - target_points_z[0, 2]
    #     # add statement to assert dz remains constant
    #     efficiency = dB / dz  
    #     unit = 'nT / m / mA'
    
    return efficiency, unit

def error(coil, target_field, target_points, target_type):
    """Compute error percentage with idealized current loops.

    coil :
        The coil object.
    target_field : array, shape (n_points, 3)
        The target field
    target_type : str
        'gradient_x' | 'gradient_y' | 'dc_x' | 'dc_y' etc.
    """
    return np.mean(
        _percent_error(coil, target_field, target_points, target_type)) * 100
