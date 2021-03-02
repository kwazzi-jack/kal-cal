import pytest
import Tigger

from kalcal.datasets.sky_models import (MODEL_1, 
        MODEL_4)


@pytest.fixture(scope="module")
def sel_LSM(n_dir):

    if n_dir == 1:
        return Tigger.load(MODEL_1)
    elif n_dir == 4:
        return Tigger.load(MODEL_4)
    else:
        raise ValueError("Only two sky-models present.")
    

@pytest.fixture(scope="module")
def n_dir(sel_LSM):
    
    return len(sel_LSM.sources)