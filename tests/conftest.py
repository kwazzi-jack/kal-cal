import pytest
import os
from .fixtures.ms import *
from .fixtures.data import *
from .fixtures.tools import *
from .fixtures.matrix import *

_dir_path = os.path.dirname(__file__)
_ms_path = os.path.join(_dir_path, "TESTING_SET.MS")

DECIMALS = 5

ANT_VARS = [7]
TIME_VARS = [2, 10, 50, 100, 200, 500, 1000]
FREQ_VARS = [1, 2, 4, 8, 16, 32]
DIR_VARS = [1, 4]
SIGMA_N_VARS = [0.0, 0.01, 0.1, 1.0]
SIGMA_F_VARS = [0.01, 0.1, 1.0]
SCALES = (0.05, 0.05, 0.5)


@pytest.fixture(params=ANT_VARS, scope="session")
def n_ant(request):
    return request.param


@pytest.fixture(params=TIME_VARS, scope="session")
def n_time(request):
    return request.param


@pytest.fixture(params=FREQ_VARS, scope="session")
def n_chan(request):
    return request.param


@pytest.fixture(params=DIR_VARS, scope="session")
def n_dir(request):
    return request.param


@pytest.fixture(scope="session")
def n_bl(n_ant):
    return n_ant * (n_ant - 1)//2


@pytest.fixture(scope="session")
def n_row(n_bl, n_time):
    return n_bl * n_time


@pytest.fixture(params=SIGMA_N_VARS, scope="session")
def sigma_n(request):
    return request.param


@pytest.fixture(params=SIGMA_F_VARS, scope="session")
def sigma_f(request):
    return request.param


@pytest.fixture(scope="session")
def length_scales():
    return SCALES


@pytest.fixture(scope="session")
def ms_name():
    """Session level fixture for test data path."""

    return _ms_path