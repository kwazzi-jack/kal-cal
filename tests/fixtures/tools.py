import pytest
import numpy as np
from .ms import n_time, n_ant, n_chan
from .lsm import n_dir


@pytest.fixture(scope="module")
def time_choice(n_time):
    return np.random.randint(0, n_time)


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