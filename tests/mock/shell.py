import numpy as np


def time_variables(
    n_time,
    n_ant
):
    """Create the time-bin indices and counts arrays
    that would be extracted from an MS."""
    tbin_indices = np.zeros(n_time, dtype=np.int32)
    tbin_counts = np.zeros(n_time, dtype=np.int32)

    n_bl = n_ant * (n_ant - 1)//2

    for t in range(n_time):
        tbin_indices[t] = t * n_bl
        tbin_counts[t] = n_bl

    return tbin_indices, tbin_counts


def antenna_pairs(
    n_time,
    n_ant,
    half='upper'
):
    """Create antenna pair arrays based on the
    upper or lower triangle indices."""

    index_func = None
    k = 0
    if half == 'upper':
        index_func = np.triu_indices
        k = 1
    elif half == 'lower':
        index_func = np.tril_indices

    ant1 = []
    ant2 = []
    for p, q in zip(*index_func(n_ant, k)):
        if p != q:
            ant1.append(p)
            ant2.append(q)
        
    return (np.tile(ant1, n_time), 
        np.tile(ant2, n_time))


def vis_shell(
    n_time,
    n_ant,
    n_chan
):
    """Create a shell of a vis matrix based
    on the parsed dimensions."""

    n_bl = n_ant * (n_ant - 1)//2
    n_row = n_time * n_bl
    vis = np.ones((n_row, n_chan),
                        dtype=np.complex128)
    
    return vis


def model_shell(
    n_time,
    n_ant,
    n_chan,
    n_dir
):
    """Create a shell of a model matrix based
    on the parsed dimensions."""

    n_bl = n_ant * (n_ant - 1)//2
    n_row = n_time * n_bl
    model = np.ones((n_row, n_chan, n_dir),
                        dtype=np.complex128)
    
    return model


def weight_shell(
    n_time,
    n_ant
):
    """Create a shell of a weight matrix based
    on the parsed dimensions."""

    n_bl = n_ant * (n_ant - 1)//2
    n_row = n_time * n_bl
    weight = np.ones((n_row), dtype=np.complex128)
    
    return weight


def jones_shell(
    n_time,
    n_ant,
    n_chan,
    n_dir,
    augment=True
):
    """Create a shell of an jones matrix based
    on the parsed dimensions. Option to augment
    the matrix."""

    jones = np.ones((n_time, n_ant, n_chan, n_dir),
                            dtype=np.complex128)
        
    jones += 1.0j * jones

    if augment:
        jones = np.stack((jones, jones.conj()), axis=4)

    return jones  


def data(
    n_time, 
    n_ant, 
    n_chan, 
    n_dir
):
    """Create mock data that contains the shell (i.e. the
    shapes) to check data-types, shapes and other properties
    not relating to physical data."""

    tbin_indices, tbin_counts = time_variables(n_time, n_ant)
    antenna1, antenna2 = antenna_pairs(n_time, n_ant)
    jones = jones_shell(n_time, n_ant, n_chan, n_dir, 
                            augment=True)
    model = model_shell(n_time, n_ant, n_chan, n_dir)
    weight = weight_shell(n_time, n_ant)
    
    return (model, weight, jones, antenna1, antenna2,
            tbin_indices, tbin_counts)   