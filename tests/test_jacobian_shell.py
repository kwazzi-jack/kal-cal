import numpy as np
from numba import njit
import pytest

from kalcal.mocktools import shell
from kalcal.mocktools import params
from kalcal.tools.jacobian import (compute_aug_coo, 
    compute_aug_csr, compute_aug_np)


shell_config = {
    "n_time" : [10, 100, 200, 500, 1000, 1500],
    "n_ant"  : [7],
    "n_chan" : [1, 2, 4, 8, 16, 32, 64],
    "n_dir"  : [1, 4, 8]
}

shell_params = params.all(shell_config)


@pytest.fixture(scope='session')
def ms_dir(tmp_path_factory):
    dest = tmp_path_factory.mktemp('ms')
    return dest


@njit(fastmath=True, nogil=True)
def jac_shape(n_ant, n_chan, n_dir):
    """Calculate the jacobian matrix shape based
    on the given data dimensions."""

    return (n_chan * n_ant * (n_ant - 1),
                2 * n_chan * n_dir * n_ant)


@njit(fastmath=True, nogil=True)
def jac_nnz(n_ant, n_chan, n_dir):
    """Calculate the number of non-zero elements
    in a jacobian with given data dimensions."""

    return 2 * n_chan * n_dir * n_ant * (n_ant - 1)
    

# ~~!~~ TESTS ~~!~~
@pytest.mark.parametrize(
    "n_time,n_ant,n_chan,n_dir", shell_params)
def test_coo_shell(
    n_time, 
    n_ant, 
    n_chan, 
    n_dir
):    
    times = np.random.randint(0, n_time, size=3)
    shape = jac_shape(n_ant, n_chan, n_dir)
    nnz = jac_nnz(n_ant, n_chan, n_dir)

    (model, weight, jones, ant1, ant2,
        tbin_indices, tbin_counts) =\
        shell.data(n_time, n_ant, n_chan, n_dir)

    for k in times:
        # Slice indices
        start = tbin_indices[k]
        end = start + tbin_counts[k]
        
        # Calculate Slices
        row_slice = slice(start, end)
        model_slice = model[row_slice]
        weight_slice = weight[row_slice]
        ant1_slice = ant1[row_slice]
        ant2_slice = ant2[row_slice]
        jones_slice = jones[k] 

        jac_coo = compute_aug_coo(model_slice, weight_slice, 
            jones_slice, ant1_slice, ant2_slice)

        assert jac_coo.data.dtype == np.complex128
        assert jac_coo.shape == shape
        assert jac_coo.nnz == nnz


@pytest.mark.parametrize(
    "n_time,n_ant,n_chan,n_dir", shell_params)
def test_csr_shell(
    n_time, 
    n_ant, 
    n_chan, 
    n_dir):

    times = np.random.randint(0, n_time, size=3)
    shape = jac_shape(n_ant, n_chan, n_dir)
    nnz = jac_nnz(n_ant, n_chan, n_dir)

    (model, weight, jones, ant1, ant2,
        tbin_indices, tbin_counts) =\
        shell.data(n_time, n_ant, n_chan, n_dir)

    for k in times:
        # Slice indices
        start = tbin_indices[k]
        end = start + tbin_counts[k]
        
        # Calculate Slices
        row_slice = slice(start, end)
        model_slice = model[row_slice]
        weight_slice = weight[row_slice]
        ant1_slice = ant1[row_slice]
        ant2_slice = ant2[row_slice]
        jones_slice = jones[k] 

        jac_csr = compute_aug_csr(model_slice, weight_slice, 
            jones_slice, ant1_slice, ant2_slice)

        assert jac_csr.data.dtype == np.complex128
        assert jac_csr.shape == shape
        assert jac_csr.nnz == nnz


@pytest.mark.parametrize(
    "n_time,n_ant,n_chan,n_dir", shell_params)
def test_np_shell(
    n_time, 
    n_ant, 
    n_chan, 
    n_dir):

    times = np.random.randint(0, n_time, size=3)
    shape = jac_shape(n_ant, n_chan, n_dir)
    
    (model, weight, jones, ant1, ant2,
        tbin_indices, tbin_counts) =\
        shell.data(n_time, n_ant, n_chan, n_dir)

    for k in times:
        # Slice indices
        start = tbin_indices[k]
        end = start + tbin_counts[k]
        
        # Calculate Slices
        row_slice = slice(start, end)
        model_slice = model[row_slice]
        weight_slice = weight[row_slice]
        ant1_slice = ant1[row_slice]
        ant2_slice = ant2[row_slice]
        jones_slice = jones[k] 

        jac_np = compute_aug_np(model_slice, weight_slice, 
            jones_slice, ant1_slice, ant2_slice)

        assert jac_np.dtype == np.complex128
        assert jac_np.shape == shape