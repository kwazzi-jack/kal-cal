import pytest
import os

_dir_path = os.path.dirname(__file__)
ms_path = os.path.join(_dir_path, "TESTING_SET.MS")


@pytest.fixture(scope="session")
def ms_name():
    """Session level fixture for test data path."""

    return str(ms_path)
