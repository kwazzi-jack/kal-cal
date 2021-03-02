import numpy as np
import pytest

from .tools import data_slice

from kalcal.tools.jacobian import (compute_aug_coo, 
    compute_aug_csr, compute_aug_np)


@pytest.fixture(scope='module')
def jac_coo(data_slice):
    _, model, weight, ant1, ant2, jones = data_slice

    return compute_aug_coo(model, weight, 
        jones, ant1, ant2)


@pytest.fixture(scope='module')
def jac_csr(data_slice):
    _, model, weight, ant1, ant2, jones = data_slice

    return compute_aug_csr(model, weight, 
        jones, ant1, ant2)


@pytest.fixture(scope='module')
def jac_np(data_slice):
    _, model, weight, ant1, ant2, jones = data_slice

    return compute_aug_np(model, weight, 
        jones, ant1, ant2)