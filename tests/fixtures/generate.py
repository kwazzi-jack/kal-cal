from numpy.core.numeric import full
import pytest
from os import path
from simms import simms
from kalcal.datasets.antenna_tables import KAT7


@pytest.fixture(scope="session")
def generate_ms(tmpdir_factory):
    folder = tmpdir_factory.mktemp("tmp")
    full_path = str(folder.join("TESTING_SET.MS"))
    print("===================>", full_path)
    simms.create_empty_ms(
        msname=full_path,
        tel='kat-7',
        pos_type='ascii',
        pos=KAT7,
        dec="-30d0m0s",
        ra="0h0m0s",
        synthesis=5,
        dtime=18,
        freq0="1.4GHz",
        nchan="8",
        dfreq="10MHz",
        stokes="RR RL LR LL",
        scan_length=["5"],
        nolog=True)

    return full_path