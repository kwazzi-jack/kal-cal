import numpy as np
from numba import njit
import pytest

from kalcal.mocktools import full
from kalcal.mocktools import params
from kalcal.tools.jacobian import (compute_aug_coo, 
    compute_aug_csr, compute_aug_np)

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

full_params = params.append(full_config, 
                    extra_config, index=0)


@pytest.fixture(scope='session')
def ms_dir(tmp_path_factory):
    dest = tmp_path_factory.mktemp('ms')
    return dest
    

# ~~!~~ TESTS ~~!~~

@pytest.mark.parametrize(
    "n_time,n_ant,n_chan,n_dir,"\
    + "sigma_n,sigma_f,seed,len_scales", full_params)
def test_coo_full(
    n_time, 
    n_ant, 
    n_chan, 
    n_dir,
    sigma_n,
    sigma_f,
    seed,
    len_scales,
    ms_dir):

    times = np.random.randint(0, n_time, size=3)
    
    (model, weight, jones, ant1, ant2,
        tbin_indices, tbin_counts) =\
        full.data(n_time, n_ant, n_chan, n_dir,
            sigma_n, sigma_f, seed, len_scales, ms_dir)

    # for k in times:
    #     # Slice indices
    #     start = tbin_indices[k]
    #     end = start + tbin_counts[k]
        
    #     # Calculate Slices
    #     row_slice = slice(start, end)
    #     model_slice = model[row_slice]
    #     weight_slice = weight[row_slice]
    #     ant1_slice = ant1[row_slice]
    #     ant2_slice = ant2[row_slice]
    #     jones_slice = jones[k] 

    #     jac_coo = compute_aug_coo(model_slice, weight_slice, 
    #         jones_slice, ant1_slice, ant2_slice)

    #     assert jac_coo.data.dtype == np.complex128