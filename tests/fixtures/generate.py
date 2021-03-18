from numpy.core.numeric import full
import pytest
import os
from simms import simms
from kalcal.datasets.antenna_tables import KAT7
import yaml
import packratt
import tarfile


# @pytest.fixture(scope="session")
# def generate_ms(tmpdir_factory):
#     folder = tmpdir_factory.mktemp("tmp")
#     full_path = str(folder.join("TESTING_SET.MS"))
#     print("===================>", full_path)
#     simms.create_empty_ms(
#         msname=full_path,
#         tel='kat-7',
#         pos_type='ascii',
#         pos=KAT7,
#         dec="-30d0m0s",
#         ra="0h0m0s",
#         synthesis=5,
#         dtime=18,
#         freq0="1.4GHz",
#         nchan="8",
#         dfreq="10MHz",
#         stokes="RR RL LR LL",
#         scan_length=["5"],
#         nolog=True)

#     return full_path


@pytest.fixture(scope="session")
def generate_ms(tmpdir_factory):

    with open("tests/custom_registry.yaml", 'r') as file:
        entry = yaml.safe_load(file)
    
    config_path = os.path.expanduser('~/.config/packratt/')
    reg_path = os.path.join(config_path, "registry.yaml")
    try:
        os.mkdir(config_path)
    except:
        pass
    
    with open(reg_path, 'w') as file:
        yaml.safe_dump(entry, file)

    folder = tmpdir_factory.mktemp("tmp")
    packratt.get('MSC_DATA/MS/KAT7_100_7_8.tar.gz', folder)

    return str(folder/"KAT7_100_7_8.MS")