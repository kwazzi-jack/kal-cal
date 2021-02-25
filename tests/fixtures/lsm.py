import pytest
import Tigger

from kalcal.datasets.sky_models import (MODEL_1, 
        MODEL_4)


DIR_VARS = [1, 4]


@pytest.fixture(params=DIR_VARS, scope="module")
def sel_LSM(request):

    if request.param == 1:
        return Tigger.load(MODEL_1)
    elif request.param == 4:
        return Tigger.load(MODEL_4)
    else:
        raise ValueError("Only two sky-models present.")
    

@pytest.fixture(scope="module")
def n_dir(sel_LSM):
    
    return len(sel_LSM.sources)