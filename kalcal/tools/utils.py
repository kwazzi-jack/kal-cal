from dask.optimization import inline
from numba import jit, prange
import numpy as np
import dask.array as da
import os


def progress_bar(head, n_time, k):
    width, _ = os.get_terminal_size()
    bar_len = width//5
    total = n_time - 1
    filled_len = int(round(bar_len*k/float(n_time - 1)))
    bar = u"\u2588" * filled_len + ' '\
            * (bar_len - filled_len)
    print("\r%s%d%%|%s| %d/%d" % (head, k/total*100, 
                                bar, k, total), end="")


def concat_dir_axis(ms, model_columns):
    """Special function to concatenate
    all the sources in the MS by along
    the direction axis."""

    sources = [ms.get(c).data for c in model_columns]
    
    n_row, n_chan, n_corr  = sources[0].shape
    n_dir = len(sources)

    model = np.zeros((n_row, n_chan, n_dir, n_corr), dtype=np.complex128)
    for d, source in enumerate(sources):
        model[:, :, d] = source.compute()
    
    # Return Dask form
    return da.from_array(model, chunks=model.shape)


@jit(nopython=True, fastmath=True, nogil=True)
def gains_reshape(g, shape):
    """Reshape the state-vector (gains) back to
    jones-format."""

    n_ant, n_chan, n_dir, _ = shape
    row_shape = n_ant * n_chan * n_dir
    m = np.zeros((n_ant, n_chan, n_dir, 2), dtype=np.complex128)

    for a in range(n_ant):
        for nu in range(n_chan):
            for s in range(n_dir):      
                row = a + n_ant * s + n_ant * n_dir * nu                
                m[a, nu, s, 0] = g[row]
                m[a, nu, s, 1] = g[row + row_shape]

    return m


@jit(nopython=True, fastmath=True, nogil=True)
def gains_vector(m):
    """Create stacked gains vector using the
    state vector."""

    n_ant, n_chan, n_dir, _ = m.shape
    row_shape = n_ant * n_chan * n_dir
    g = np.zeros((2*row_shape), dtype=np.complex128)

    for a in range(n_ant):
        for nu in range(n_chan):
            for s in range(n_dir):
                row = a + n_ant * s + n_ant * n_dir * nu                
                g[row] = m[a, nu, s, 0]
                g[row + row_shape] = m[a, nu, s, 1]
    
    return g


@jit(nopython=True, fastmath=True, nogil=True)
def measure_vector(vis_data, weight, n_ant, n_chan):
    """Create stacked measurement vector using visibility
    data from the measurement."""

    n_bl = n_ant * (n_ant - 1)//2
    row_shape = n_chan * n_ant * (n_ant - 1)
    y = np.zeros(row_shape, dtype=np.complex128)

    n_row = vis_data.shape[0]

    for row in range(n_row):
        sqrtW = np.sqrt(weight[row])
        data = vis_data[row]
        for nu in range(n_chan):            
            row_upper = 2 * n_bl * nu + row % n_bl
            row_lower = row_upper + n_bl
            y[row_upper] = sqrtW * data[nu]
            y[row_lower] = sqrtW * data[nu].conjugate()

    return y


@jit(nopython=True, fastmath=True, nogil=True)
def true_gains_vector(m):
    """Create stacked gains vector, but using the
    true jones rather than a state-vector for debug
    -ing purposes."""

    n_ant, n_chan, n_dir = m.shape
    row_shape = n_ant * n_chan * n_dir
    g = np.zeros((2 * row_shape), dtype=np.complex128)

    for s in range(n_dir):
        for nu in range(n_chan):        
            for a in range(n_ant):
                row = a + n_ant * s + n_ant * n_dir * nu                
                g[row] = m[a, nu, s]
                g[row + row_shape] = m[a, nu, s].conj()

    return g


@jit(nopython=True, fastmath=True,
        nogil=True, cache=True, inline="always")
def diag_mat_dot_mat(
    A : np.ndarray, 
    B : np.ndarray
    ):

    """Perform a dot product for diagonal elements
    only on the two matrices A and B, and return 
    the answer as a 1D array. Note, the theoretical dot
    product result should also be square.

    Args:
        A (numpy.ndarray): Left-most matrix with shape (n, m).
        B (numpy.ndarray): Right-most matrix with shape (m, n).

    Returns:
        C (numpy.ndarray): Diagonal of dot product
        between A and B with shape (n,).
    """

    # Extract dimension sizes
    n, m = A.shape
    
    # Check dimensions
    if B.shape != (m, n):
        raise ValueError("Matrix dimensions do not form square "\
                            + "matrix after dot-product.")    

    # Array to keep result
    C = np.zeros(n, dtype=A.dtype)

    # Perform diagonal dot product
    for i in range(n):
        for j in range(m):
            C[i] += A[i, j] * B[j, i]

    # Return result
    return C


@jit(nopython=True, fastmath=True, nogil=True)
def diag_cov_reshape(P, shape):

    return gains_reshape(np.diag(P), shape).real

    
@jit(nopython=True, fastmath=True, nogil=True)
def diag_cov_flatten(P):

    return np.diag(gains_vector(P).real)


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