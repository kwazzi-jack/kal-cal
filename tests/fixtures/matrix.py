import numpy as np
import pytest

from .tools import data_slice

from kalcal.tools.jacobian import (compute_aug_coo, 
    compute_aug_csr, compute_aug_np)
from kalcal.tools.utils import (gains_vector, measure_vector)


@pytest.fixture(scope='module')
def jac_coo(data_slice):
    _, _, model, weight, ant1, ant2, jones = data_slice

    return compute_aug_coo(model, weight, 
        jones, ant1, ant2)


@pytest.fixture(scope='module')
def jac_csr(data_slice):
    _, _, model, weight, ant1, ant2, jones = data_slice

    return compute_aug_csr(model, weight, 
        jones, ant1, ant2)


@pytest.fixture(scope='module')
def jac_np(data_slice):
    _, _, model, weight, ant1, ant2, jones = data_slice

    return compute_aug_np(model, weight, 
        jones, ant1, ant2)


@pytest.fixture(scope='module')
def clean_meas_vec(data_slice, n_ant, n_chan):
    clean_vis, _, _, weight, _, _, _ = data_slice
    return measure_vector(clean_vis, weight, n_ant, n_chan)


@pytest.fixture(scope='module')
def true_state_vec(data_slice):
    jones = data_slice[-1]
    return gains_vector(jones)