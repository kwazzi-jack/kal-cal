import pytest
import Tigger

from kalcal.datasets.sky_models import (MODEL_1, 
        MODEL_4)


DIR_VARS = [MODEL_1, MODEL_4]


@pytest.fixture(params=DIR_VARS, scope="module")
def sel_LSM(request):

    return Tigger.load(request.param)


@pytest.fixture(scope="module")
def n_dir(sel_LSM):
    
    return len(sel_LSM.sources)