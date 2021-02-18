from numba import jit
import numpy as np
import dask.array as da


def concat_dir_axis(ms):
    """Special function to concatenate
    all the sources in the MS by along
    the direction axis."""

    sources = []
    i = 0
    
    while True:
        try:
            source = ms.get(f'J{i}').data
            sources.append(source)
            i += 1
        except:
            break
    
    n_row, n_chan, n_corr  = sources[0].shape
    n_dir = len(sources)

    model = np.zeros((n_row, n_chan, n_dir, n_corr), dtype=np.complex128)
    for d, source in enumerate(sources):
        model[:, :, d] = source.compute()
    
    # Return Dask form
    return da.from_array(model, chunks=model.shape)


@jit(nopython=True, fastmath=True)
def gains_reshape(g, shape):
    """Reshape the state-vector (gains) back to
    jones-format."""

    n_ant, n_chan, n_dir, _ = shape
    row_shape = n_ant * n_chan * n_dir
    m = np.zeros((n_ant, n_chan, n_dir, 2), dtype=np.complex128)

    for nu in range(n_chan):
        for s in range(n_dir):
            for a in range(n_ant):
                row = a + n_ant * s + n_ant * n_dir * nu                
                m[a, nu, s, 0] = g[row]
                m[a, nu, s, 1] = g[row + row_shape]

    return m


@jit(nopython=True, fastmath=True)
def gains_vector(m):
    """Create stacked gains vector using the
    state vector."""

    n_ant, n_chan, n_dir, _ = m.shape
    row_shape = n_ant * n_chan * n_dir
    g = np.zeros((2*row_shape), dtype=np.complex128)

    for nu in range(n_chan):
        for s in range(n_dir):
            for a in range(n_ant):
                row = a + n_ant * s + n_ant * n_dir * nu                
                g[row] = m[a, nu, s, 0]
                g[row + row_shape] = m[a, nu, s, 1]
    
    return g


@jit(nopython=True, fastmath=True)
def measure_vector(vis_data, weight, n_ant, n_chan):
    """Create stacked measurement vector using visibility
    data from the measurement."""

    n_bl = n_ant * (n_ant - 1)//2
    row_shape = n_chan * n_ant * (n_ant - 1)
    y = np.zeros(row_shape, dtype=np.complex128)

    n_row = vis_data.shape[0]

    for row in range(n_row):
        sqrtW = np.sqrt(weight[row])
        for nu in range(n_chan):
            data = vis_data[row, nu]
            row_upper = 2 * n_bl * nu + row % n_bl
            row_lower = row_upper + n_bl
            y[row_upper] = sqrtW * data
            y[row_lower] = sqrtW * data.conjugate()

    return y


@jit(nopython=True, fastmath=True)
def true_gains_vector(m):
    """Create stacked gains vector, but using the
    true jones rather than a state-vector for debug
    -ing purposes."""

    n_ant, n_chan, n_dir = m.shape
    row_shape = n_ant * n_chan * n_dir
    g = np.zeros((2*row_shape), dtype=np.complex128)

    for nu in range(n_chan):
        for s in range(n_dir):
            for a in range(n_ant):
                row = a + n_ant * s + n_ant * n_dir * nu                
                g[row] = m[a, nu, s]
                g[row + row_shape] = m[a, nu, s].conj()

    return g


def state_ensemble(m, C, N=10):
    """Create an ensemble matrix of states, M, by drawing
    N-samples from filter distribution (m, C), joining
    each sample is by column."""

    M = np.random.multivariate_normal(m.real, C.real, size=N)\
        + 1.0j * np.random.multivariate_normal(m.imag, C.real, size=N)

    return M.T


def measure_noise(R, N=10):
    """Create an ensemble matrix of measurements, Y, by
    drawing N-samples from a white-noise distribution (0, R),
    joining each sample is by column."""

    m = np.zeros(R.shape[0])

    e = np.random.multivariate_normal(m, R.real, size=N)\
        + 1.0j * np.random.multivariate_normal(m, cov=R.real, size=N)

    return e.T


def process_noise(Q, N=10):
    m = np.zeros(Q.shape[0])

    e = np.random.multivariate_normal(m, Q.real, size=N)\
        + 1.0j * np.random.multivariate_normal(m, cov=Q.real, size=N)

    return e.T