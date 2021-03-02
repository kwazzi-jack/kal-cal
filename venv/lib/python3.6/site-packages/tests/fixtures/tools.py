import pytest
import numpy as np
from .data import load_data


@pytest.fixture(scope="module")
def jac_shape(n_ant, n_chan, n_dir):
    """Calculate the jacobian matrix shape based
    on the given data dimensions."""

    return (n_chan * n_ant * (n_ant - 1),
                2 * n_chan * n_dir * n_ant)


@pytest.fixture(scope="module")
def jac_nnz(n_ant, n_chan, n_dir):
    """Calculate the number of non-zero elements
    in a jacobian with given data dimensions."""

    return 2 * n_chan * n_dir * n_ant * (n_ant - 1)


@pytest.fixture(scope="module")
def time_choice(n_time):
    return np.random.randint(0, n_time)


@pytest.fixture(scope="module")
def data_slice(time_choice, load_data):

    tbin_indices, tbin_counts, ant1, ant2,\
            clean_vis, vis, model, weight, jones = load_data

    k = time_choice

    # Slice indices
    start = tbin_indices[k]
    end = start + tbin_counts[k]
    
    # Calculate Slices
    row_slice = slice(start, end)
    clean_slice = clean_vis[row_slice]
    vis_slice = vis[row_slice]
    model_slice = model[row_slice]
    weight_slice = weight[row_slice]
    ant1_slice = ant1[row_slice]
    ant2_slice = ant2[row_slice]
    jones_slice = jones[k]

    return (clean_slice, vis_slice, model_slice, weight_slice,
            ant1_slice, ant2_slice, jones_slice)