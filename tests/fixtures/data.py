import pytest
import numpy as np
from daskms import xds_from_table

@pytest.fixture
def ms_dir(tmp_path_factory):
    return 

@pytest.fixture
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


@pytest.fixture
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