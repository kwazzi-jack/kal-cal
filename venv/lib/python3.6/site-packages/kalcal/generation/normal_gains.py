import numpy as np
from africanus.gps.kernels import exponential_squared as expsq
from africanus.linalg import kronecker_tools as kt
from tqdm import tqdm


def normal_gains(t, nu, s, n_ant, n_corr, sigmaf, lt, lnu, ls):
    """Produce normal complex-gains based on the dimensions given."""

    # Dask to NP
    t = t.compute()
    
    # Scale down domain
    t = t/t.max()    
    nu = nu/nu.max()

    # Catch one-direction case
    if s.max() != 0:
        s = s/s.max()
    
    # Get dimensions
    n_time = t.size
    n_chan = nu.size
    n_dir = s.shape[0]

    # Make prior covariace matrices
    Kt = expsq(t, t, sigmaf, lt)
    Knu = expsq(nu, nu, 1.0, lnu)
    Ks = expsq(s, s, 1.0, ls)

    # Stack and get cholesky factors
    K = np.array((Kt, Knu, Ks), dtype=object)
    L = kt.kron_cholesky(K)

    # Simulate independent gain per antenna and direction
    gains = np.zeros((n_time, n_ant, n_chan, 
                n_dir, n_corr), dtype=np.complex128)
    
    for p in tqdm(range(n_ant)):
        for c in range(n_corr):
            # Generate random complex vector
            xi = np.random.randn(n_time, n_chan, n_dir)/np.sqrt(2)\
                    + 1.0j * np.random.randn(n_time, n_chan, n_dir)/np.sqrt(2)

            # Apply to field
            gains[:, p, :, :, c] = \
                kt.kron_matvec(L, xi).reshape(n_time, n_chan, n_dir) + 1.0

    # Return normal-form gains
    return gains