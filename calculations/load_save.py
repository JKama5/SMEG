import pickle

def save_coil_mesh(vertices, faces, filename='coilmesh1.pkl'):
    """Save the coil mesh vertices and faces to a file."""
    with open(filename, 'wb') as f:
        pickle.dump({'vertices': vertices, 'faces': faces}, f)

def load_coil_mesh(filename):
    """Load the coil mesh vertices and faces from a file."""
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_loops(loops, filename='loops.pkl'):
    """Save the coil windings (loops) to a file."""
    with open(filename, 'wb') as f:
        pickle.dump(loops, f)

def load_loops(filename):
    """Load the coil windings (loops) from a file."""
    with open(filename, 'rb') as f:
        return pickle.load(f)

def load_target_points(filename):
    """Load the target points from a file."""
    with open(filename, 'rb') as f:
        return pickle.load(f)