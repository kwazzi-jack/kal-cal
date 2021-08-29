import numpy as np
import Tigger
from daskms import xds_from_ms, xds_from_table
from africanus.gps.kernels import exponential_squared as expsq
from africanus.linalg import kronecker_tools as kt
from africanus.coordinates import radec_to_lm
from kalcal.tools.utils import progress_bar
from kalcal.datasets.sky_models import (
    MODEL_1, MODEL_4, MODEL_50
)
from omegaconf import OmegaConf as ocf


# Sky-model paths
sky_models = {
    "model-1"    : MODEL_1,
    "model-4"    : MODEL_4,
    "model-50"   : MODEL_50
}


def phase_gains(lm, freq, n_time, n_ant, n_chan, n_dir, n_corr, sigma_f):
    """Produce phase-only (screen) gains based on dimensions parsed in."""

    # Create basis matrix for plane [1, l, m]
    n_coeff = 3
    l_coord = lm[:, 0]
    m_coord = lm[:, 1]
    basis = np.hstack((np.ones((n_dir, 1), dtype=np.float64), 
                        l_coord[:, None], m_coord[:, None]))

    # Get coeffs
    alphas = sigma_f * np.random.randn(n_time, n_ant, n_coeff, n_corr)

    # Normalise frequencies
    freq_norm = freq/freq.min()

    # Simulate phases
    iterations = n_time * n_ant * 2
    head = f"==> Generating (iterations={iterations}): "  

    phases = np.zeros((n_time, n_ant, n_chan, n_dir, n_corr),
                        dtype=np.complex64)
    for t in range(n_time):
        for p in range(n_ant):
            for c in [0, n_corr - 1]:
                # Progress Bar
                progress_bar(head, iterations + 1, 2 * t * n_ant\
                                + 2 * p + 2)

                # Get screen at source locations
                screen = basis.dot(alphas[t, p, :, c])

                # Apply frequency scaling
                phases[t, p, :, :, c] = screen[None, :] / freq_norm[:, None]

    print()

    # Return phase-form gains
    return np.exp(1.0j * phases)


def normal_gains(t, nu, s, n_time, n_ant, n_chan, 
                    n_dir, n_corr, sigma_f, lt, lnu, ls):
    """Produce normal complex-gains based on the dimensions given."""

    # Scale down domain
    t = t/t.max() if t.max() !=0 else t    
    nu = nu/nu.max() if nu.max() != 0 else nu
    s = s/s.max() if s.max() != 0 else s

    # Make prior covariace matrices
    Kt = expsq(t, t, sigma_f, lt)
    Knu = expsq(nu, nu, 1.0, lnu)
    Ks = expsq(s, s, 1.0, ls)

    # Stack and get cholesky factors
    K = np.array((Kt, Knu, Ks), dtype=object)
    
    L = kt.kron_cholesky(K)

    # Simulate independent gain per antenna and direction
    gains = np.zeros((n_time, n_ant, n_chan, 
                n_dir, n_corr), dtype=np.complex128)
    
    iterations = n_ant * n_corr
    head = f"==> Generating (iterations={iterations}): "    
    for p in range(n_ant):
        for c in range(n_corr):
            
            # Progress Bar
            progress_bar(head, iterations + 1, p * n_corr + c + 1)

            # Generate random complex vector
            xi = np.random.randn(n_time, n_chan, n_dir)/np.sqrt(2)\
                    + 1.0j * np.random.randn(n_time, n_chan, n_dir)/np.sqrt(2)

            # Apply to field
            gains[:, p, :, :, c] = \
                kt.kron_matvec(L, xi).reshape(n_time, n_chan, n_dir) + 1.0

    print()

    # Return normal-form gains
    return gains


def new(ms, sky_model, **kwargs):
    """Generate a jones matrix based on a given sky-model
    either as phase-only or normal gains, as an .npy file."""

    # Options to attributed dictionary
    if kwargs["yaml"] is not None:
        options = ocf.load(kwargs["yaml"])
    else:    
        options = ocf.create(kwargs)    

    # Set to struct
    ocf.set_struct(options, True)

    # Change path to sky model if chosen
    try:
        sky_model = sky_models[sky_model.lower()]        
    except:
        # Own sky model reference
        pass

    # Load ms
    MS = xds_from_ms(ms)[0]

    # Get dimensions (correlations need to be adapted)
    dims = ocf.create(dict(MS.sizes))
    n_chan = dims.chan
    n_corr = dims.corr

    # Get time-bin indices and counts
    _, tbin_indices, _ = np.unique(MS.TIME,
                                        return_index=True, 
                                        return_counts=True)

    # Set time dimension
    n_time = len(tbin_indices)

    # Get antenna arrays (dask ignored for now)
    ant1 = MS.ANTENNA1.data.compute()
    ant2 = MS.ANTENNA2.data.compute()

    # Set antenna dimension
    n_ant = np.max((np.max(ant1), np.max(ant2))) + 1

    # Build source model from lsm
    lsm = Tigger.load(sky_model)

    # Set direction axis as per source
    n_dir = len(lsm.sources)

    # Get phase direction
    radec0_table = xds_from_table(ms + '::FIELD')[0]
    radec0 = radec0_table.PHASE_DIR.data.squeeze().compute()
    
    # Get frequency column
    freq_table = xds_from_table(ms + '::SPECTRAL_WINDOW')[0]
    freq = freq_table.CHAN_FREQ.data.astype(np.float64)[0]

    # Check dimension
    assert freq.size == n_chan

    # Create initial coordinate array and source names
    lm = np.zeros((n_dir, 2), dtype=np.float64)

    # Cycle coordinates creating a source with flux
    for d, source in enumerate(lsm.sources):
        # Extract position
        radec_s = np.array([[source.pos.ra, source.pos.dec]])
        lm[d] =  radec_to_lm(radec_s, radec0)

    # Direction independent gains
    if options.die:
        lm = np.array(lm[0]).reshape((1, -1))
        n_dir = 1
    
    # Choose between phase-only or normal
    if options.type == "phase":
        # Run phase-only
        print("==> Simulating `phase-only` gains, with dimensions ("\
            + f"n_time={n_time}, n_ant={n_ant}, n_chan={n_chan}, "\
            + f"n_dir={n_dir}, n_corr={n_corr})")

        jones = phase_gains(lm, freq, n_time, n_ant, 
                                n_chan, n_dir, n_corr, 
                                options.std)
        
    elif options.type == "normal":
        # With normal selected, get differentials
        lt, lnu, ls = options.diffs

        # Run normal
        print("==> Simulating `normal` gains, with dimensions ("\
            + f"n_time={n_time}, n_ant={n_ant}, n_chan={n_chan}, "\
            + f"n_dir={n_dir}, n_corr={n_corr})")
        jones = normal_gains(tbin_indices, freq, lm,
                                n_time, n_ant, n_chan, 
                                n_dir, n_corr, options.std, 
                                lt, lnu, ls)

    # Output to jones to .npy file
    gains_file = (options.type + ".npy") if options.out_file is None\
                    else options.out_file    
    
    with open(gains_file, 'wb') as file:            
            np.save(file, jones)
    print(f"==> Completed and gains saved to: {gains_file}")