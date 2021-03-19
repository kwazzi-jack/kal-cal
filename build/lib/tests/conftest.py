import pytest
import os
from .fixtures.ms import *
from .fixtures.data import *
from .fixtures.tools import *
from .fixtures.matrix import *
from .fixtures.generate import *

DECIMALS = 5

ANT_VARS = [7]
TIME_VARS = [2, 10, 15, 20, 51, 100]
FREQ_VARS = [1, 2, 4, 8]
DIR_VARS = [1, 4]
SIGMA_N_VARS = [0.1]
SIGMA_F_VARS = [1.0]
SCALES = (0.05, 0.05, 0.5)


@pytest.fixture(scope="session")
def ms_name(generate_ms):
    return generate_ms


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