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
def base_ms(tmp_path_factory, request):
    model_dir = tmp_path_factory.mktemp("model")
    key, ms_name = request.param
    ms_filename = model_dir / ms_name
    # This will download into packratt cache and then untar into model_dir
    packratt.get(key, model_dir)

    try:
        yield model_dir / ms_name
    finally:
        pass
        # Could clear up if we wanted to, but pytest also removes old runs
        # shutil.rmtree(model_dir)


@pytest.fixture(scope="function", params=[{"source": 2}])
def model_ms(base_ms, request):
    with pt.table(str(base_ms), readonly=False, ack=False) as T, \
        pt.table(str(base_ms) + "::SPECTRAL_WINDOW") as S, \
        pt.table(str(base_ms) + "::POLARIZATION") as P:

        row = T.nrows()
        assert S.nrows() == 1
        chan_freq = S.getcol("CHAN_FREQ")[0]
        num_chan = S.getcol("NUM_CHAN")[0]
        chan = chan_freq.shape[0]

        assert P.nrows() == 1
        num_corr = P.getcol("NUM_CORR")[0]

        lm = np.random.random((request.param["source"], 2))
        uvw = T.getcol("UVW")

        l = lm[:, 0, None, None]
        m = lm[:, 1, None, None]
        n = np.sqrt(1.0 - l**2 - m**2)

        u = uvw[None, :, 0, None]
        v = uvw[None, :, 1, None]
        w = uvw[None, :, 2, None]

        chan_freq = chan_freq[None, None, :]

        phase = l*u + m*v + (n - 1)*w*chan_freq/3e8
        phase = np.exp(-2*np.pi*1j*phase)
        vis = phase.sum(axis=0)

        if num_corr == 1:
            pass
        elif num_corr == 2:
            vis = np.stack([vis, vis], axis=2)
        elif num_corr == 4:
            zero = np.zeros_like(vis)
            vis = np.stack([vis, zero, zero, vis], axis=2)
        else:
            raise ValueError(f"Unhandled NUM_CORR {num_corr}")

        T.putcol("DATA", vis)

    return str(base_ms)

def test_model_ms_1(model_ms):
    with pt.table(model_ms) as ms:
        ms.getcol("DATA")

# Indirectly parametrize base_ms (key, ms_name) parameters)
@pytest.mark.parametrize("base_ms", [
    ("/test/ms/2020-06-04/google/smallest_ms.tar.gz", "smallest_ms.ms_p0")],
    indirect=True)
def test_model_ms_2(model_ms):
    with pt.table(model_ms) as ms:
        ms.getcol("DATA")
