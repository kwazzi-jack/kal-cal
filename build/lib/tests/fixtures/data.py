import pytest
import numpy as np
import Tigger
from africanus.coordinates import radec_to_lm
from africanus.dft.kernels import im_to_vis
from africanus.model.coherency.conversion import convert
from africanus.calibration.utils.corrupt_vis import corrupt_vis

from kalcal.generation.normal_gains import normal_gains

from .ms import (sel_PHASE_DIR, sel_FREQ, sel_ANTENNA,
                    sel_UVW)
from .lsm import sel_LSM


@pytest.fixture(scope="module")
def gen_time_bin_vars(sel_TIME):

    _, tbin_indices, tbin_counts\
        = np.unique(sel_TIME, return_index=True,
                        return_counts=True)
    
    return tbin_indices, tbin_counts


@pytest.fixture(scope="module")
def gen_lm(sel_PHASE_DIR, sel_LSM, n_dir):

    lm = np.zeros((n_dir, 2), dtype=np.float64)

    # Cycle coordinates creating a source with flux
    for d, source in enumerate(sel_LSM.sources):

        # Extract position
        radec_s = np.array([[source.pos.ra, source.pos.dec]])
        lm[d] =  radec_to_lm(radec_s, sel_PHASE_DIR)

    return lm


@pytest.fixture(scope="module")
def gen_JONES(gen_time_bin_vars, gen_lm, sel_FREQ, n_ant, 
                sigma_f, length_scales):

    lt, lnu, ls = length_scales
    tbin_indices, tbin_counts = gen_time_bin_vars
    jones = normal_gains(tbin_indices, sel_FREQ, gen_lm, 
                n_ant, 4, sigma_f, lt, lnu, ls)
    
    jones = jones[:, :, :, :, (0, -1)]

    # Jones to complex
    return jones.astype(np.complex128)


@pytest.fixture(scope="module")
def gen_MODEL_DATA(sel_FREQ, sel_UVW, sel_LSM, 
                    gen_lm, n_chan, n_row, n_dir):

    # Create initial model array
    model = np.zeros((n_dir, n_chan, 4), dtype=np.float64)

    # Cycle coordinates creating a source with flux
    for d, source in enumerate(sel_LSM.sources):
        flux = getattr(source, 'flux')
        for i, stokes in enumerate(['I', 'Q', 'U', 'V']):
            stokes_val = getattr(flux, stokes)
            if stokes_val:
                # Get spectrum (only spi currently supported)
                tmp_spec = source.spectrum
                spi = [tmp_spec.spi if tmp_spec 
                            is not None else 0.0]
                ref_freq = [tmp_spec.freq0 if tmp_spec 
                                    is not None else 1.0]
    
                # Generate model flux
                model[d, :, i] = stokes_val\
                    * (sel_FREQ/ref_freq)**spi

    # Get model visibilities
    model_vis = np.zeros((n_row, n_chan, n_dir, 4), 
                            dtype=np.complex128)
    for s in range(n_dir):
        model_vis[:, :, s] = im_to_vis(
            model[s].reshape((1, n_chan, 4)),
            sel_UVW, 
            gen_lm[s].reshape((1, 2)), 
            sel_FREQ, 
            dtype=np.complex64)

    # Convert Stokes to corr
    in_schema = ['I', 'Q', 'U', 'V']
    out_schema = [['RR', 'RL'], ['LR', 'LL']]
    model_vis = convert(model_vis, in_schema, out_schema)

    return model_vis


@pytest.fixture(scope="module")
def reshaped_MODEL_DATA(gen_MODEL_DATA, n_row, 
                            n_chan, n_dir):

    return gen_MODEL_DATA.reshape(
            n_row, n_chan, n_dir, 4)


@pytest.fixture(scope="module")
def gen_CLEAN_VIS_DATA(gen_time_bin_vars, gen_JONES,
         gen_MODEL_DATA, sel_ANTENNA):
    tbin_indices, tbin_counts = gen_time_bin_vars
    ant1, ant2 = sel_ANTENNA
    jones = gen_JONES
    model = gen_MODEL_DATA
    
    data = corrupt_vis(tbin_indices, tbin_counts, 
                        ant1, ant2, jones, model)

    return data


@pytest.fixture(scope="module")
def reshaped_CLEAN_VIS_DATA(gen_CLEAN_VIS_DATA, 
        n_row, n_chan):

    return gen_CLEAN_VIS_DATA.reshape(
            n_row, n_chan, 4)


@pytest.fixture(scope="module")
def gen_NOISE(sigma_n, n_row, n_chan):
    
    noise = np.random.normal(loc=0.0, scale=sigma_n,
                size=(n_row, n_chan, 4))\
            + 1.0j*np.random.normal(loc=0.0, 
                scale=sigma_n, size=(n_row, n_chan, 4))
                
    ZERO = np.zeros((n_row, n_chan), dtype=noise.dtype)
    noise[:, :, 1] = ZERO
    noise[:, :, 2] = ZERO

    return noise/np.sqrt(2)


@pytest.fixture(scope="module")
def gen_VIS_DATA(reshaped_CLEAN_VIS_DATA, gen_NOISE):
    
    data = reshaped_CLEAN_VIS_DATA + gen_NOISE
    
    return data.astype(np.complex128)


@pytest.fixture(scope="module")
def gen_WEIGHT(n_row):
    
    return np.ones(n_row, dtype=np.complex128)


@pytest.fixture(scope="module")
def load_data(gen_time_bin_vars, sel_ANTENNA, 
        reshaped_CLEAN_VIS_DATA,
        gen_VIS_DATA, reshaped_MODEL_DATA,
        gen_WEIGHT, gen_JONES):

    tbin_indices, tbin_counts = gen_time_bin_vars       
    ant1, ant2 = sel_ANTENNA
    clean_vis = reshaped_CLEAN_VIS_DATA[:, :, 0]
    vis = gen_VIS_DATA[:, :, 0] #remove correlations
    model = reshaped_MODEL_DATA[:, :, :, 0] #remove correlations
    weight = gen_WEIGHT
    gen_JONES[:, :, :, :, 1] = gen_JONES[:, :, :, :, 0].conj()
    jones = gen_JONES
    return tbin_indices, tbin_counts, ant1, ant2,\
            clean_vis, vis, model, weight, jones