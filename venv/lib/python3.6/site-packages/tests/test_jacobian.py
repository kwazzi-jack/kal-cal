import numpy as np
from numba import njit
import pytest

from final.tests.mock import shell
from final.tests.mock import full
from final.tests.mock import params
from final.tools.jacobian import (compute_aug_coo, 
    compute_aug_csr, compute_aug_np)


shell_config = {
    "n_time" : [10, 100, 200, 500, 1000, 1500],
    "n_ant"  : [7],
    "n_chan" : [1, 2, 4, 8, 16, 32, 64],
    "n_dir"  : [1, 4, 8]
}

full_config = {
    "n_time"  : [10, 100, 200, 500, 1000, 1500],
    "n_ant"   : [7],
    "n_chan"  : [1, 2, 4, 8, 16, 32, 64],
    "n_dir"   : [1, 4, 8],
    "sigma_n" : [0.0, 0.1, 0.5, 0.75, 1.0],
    "sigma_f" : [0.01, 0.1, 0.2, 0.5, 1.0],
    "seed"    : [42, 666]
}

extra_config = {
    10 : (0.1, 0.1, 0.5),
    100 : (0.09, 0.09, 0.5),
    200 : (0.08, 0.08, 0.5),
    500 : (0.07, 0.07, 0.5),
    1000 : (0.05, 0.05, 0.5),
    1500 : (0.02, 0.02, 0.5),
}

shell_params = params.all(shell_config)
full_params = params.append(full_config, 
               extra_config, index=0)

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
    n_dir,
    tmp_path_factory
):
    dest = tmp_path_factory.mkdir('ms')
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


# @pytest.mark.parametrize(
#     "n_time,n_ant,n_chan,n_dir", shell_params)
# def test_coo_full(
#     n_time, 
#     n_ant, 
#     n_chan, 
#     n_dir):

#     times = np.random.randint(0, n_time, size=3)

#     (model, weight, jones, ant1, ant2,
#         tbin_indices, tbin_counts) =\
#         shell.data(n_time, n_ant, n_chan, n_dir)

#     for k in times:
#         # Slice indices
#         start = tbin_indices[k]
#         end = start + tbin_counts[k]
        
#         # Calculate Slices
#         row_slice = slice(start, end)
#         model_slice = model[row_slice]
#         weight_slice = weight[row_slice]
#         ant1_slice = ant1[row_slice]
#         ant2_slice = ant2[row_slice]
#         jones_slice = jones[k] 

#         jac_coo = compute_aug_coo(model_slice, weight_slice, 
#             jones_slice, ant1_slice, ant2_slice)

#         assert jac_coo.data.dtype == np.complex128
#         assert jac_coo.shape == shape
#         assert jac_coo.nnz == nnz


@pytest.mark.parametrize(
    "n_time,n_ant,n_chan,n_dir", shell_params)
def test_coo_shell(
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