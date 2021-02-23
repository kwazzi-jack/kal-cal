import shutil
import tarfile

import numpy as np
import packratt
import pytest
import pyrap.tables as pt


# This fixture has a function "scope" -- it is re-run for each test function
# other options include "module" and "session"
# "params" define the fixture arguments which are passed to the fixture
# in request.param. Here I've defined a default key, ms pair.
# This can be indirectly set in individual test cases,
# see test_model_ms_2
@pytest.fixture(scope="function", params=[
        ("/test/ms/2020-06-04/elwood/smallest_ms.tar.gz",
        "smallest_ms.ms_p0")
    ])
def model_ms(tmp_path_factory, request):
    model_dir = tmp_path_factory.mktemp("model")
    key, ms_name = request.param
    ms_filename = model_dir / ms_name
    # This will download into packratt cache and then untar into model_dir
    packratt.get(key, model_dir)

    # Modify the untarred MS
    with pt.table(str(ms_filename), readonly=False, ack=False) as T:
        existing = T.getcol("DATA")
        assert np.all(existing != 256)
        T.putcol("DATA", np.full_like(existing, 256))

    try:
        yield model_dir / ms_name
    finally:
        pass
        # Could clear up if we wanted to, but pytest also removes old runs
        # shutil.rmtree(model_dir)


def test_model_ms_1(model_ms):
    with pt.table(str(model_ms)) as ms:
        assert np.all(ms.getcol("DATA") == 256)

# Indirectly parametrize model_ms (key, ms_name) parameters)
@pytest.mark.parametrize("model_ms", [
    ("/test/ms/2020-06-04/google/smallest_ms.tar.gz", "smallest_ms.ms_p0")],
    indirect=True)
def test_model_ms_2(model_ms):
    with pt.table(str(model_ms)) as ms:
        assert np.all(ms.getcol("DATA") == 256)
