import pytest
from daskms import xds_from_table
import numpy as np


@pytest.fixture(scope="module")
def full_ms_data(ms_name):
    """Load full ms into memory for pytest."""

    return xds_from_table(ms_name)[0]


@pytest.fixture(scope="module")
def full_field_data(ms_name):
    """Load full field from ms into memory 
    for pytest."""

    return xds_from_table(ms_name\
                + "::FIELD")[0]


@pytest.fixture(scope="module")
def full_spw_data(ms_name):
    """Load full spectral window from ms into 
    memory for pytest."""

    return xds_from_table(ms_name\
                + "::SPECTRAL_WINDOW")[0]


@pytest.fixture(scope="module")
def sel_TIME(n_row, full_ms_data):

    return full_ms_data.TIME.values[0:n_row]


@pytest.fixture(scope="module")
def sel_ANTENNA(n_row, full_ms_data):

    ant1 = full_ms_data.ANTENNA1.values[0:n_row]
    ant2 = full_ms_data.ANTENNA2.values[0:n_row]

    return ant1, ant2


@pytest.fixture(scope="module")
def sel_UVW(n_row, full_ms_data):

    return full_ms_data.UVW.values[0:n_row]


@pytest.fixture(scope="module")
def sel_FLAG(n_row, full_ms_data):

    return full_ms_data.FLAG.values[0:n_row]


@pytest.fixture(scope="module")
def sel_PHASE_DIR(full_field_data):

    return full_field_data.PHASE_DIR.values.ravel()


@pytest.fixture(scope="module")
def sel_FREQ(n_chan, full_spw_data):

    freq = full_spw_data.CHAN_FREQ.values[0]
    return freq[0:n_chan].astype(np.float64)