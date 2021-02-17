import packratt
import pytest

import tarfile
def test_something(tmp_path_factory):
    # Create a temporary directory with pytest's tempory path utilities
    dest = tmp_path_factory.mktemp("ms")
    # Download file
    packratt.get('/ms/foo_1.tar.gz', dest)

    print('DONE')

    assert 1 == 1

