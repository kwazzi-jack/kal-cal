import pytest
import numpy as np
import Tigger
from africanus.coordinates import radec_to_lm
from africanus.dft.kernels import im_to_vis
from africanus.model.coherency.conversion import convert

from .ms import (sel_PHASE_DIR, sel_FREQ, 
                    sel_UVW, n_chan, n_row)
from .lsm import sel_LSM, n_dir


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

    return model_vis.reshape(n_row, n_chan, n_dir, 4)