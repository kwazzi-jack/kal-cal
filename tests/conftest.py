import pytest
import os
from .fixtures.ms import *
from .fixtures.data import *
from .fixtures.tools import *
from .fixtures.matrix import *

_dir_path = os.path.dirname(__file__)
_ms_path = os.path.join(_dir_path, "TESTING_SET.MS")

DECIMALS = 5


@pytest.fixture(scope="session")
def ms_name():
    """Session level fixture for test data path."""

    return _ms_path