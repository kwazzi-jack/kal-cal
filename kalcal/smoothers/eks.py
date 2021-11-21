import numpy as np
from numba import njit, objmode
from kalcal.tools.utils import gains_vector, gains_reshape


@njit(fastmath=True, nogil=True)
def numba_algorithm(
    m : np.ndarray, 
    P : np.ndarray, 
    Q : np.ndarray):

    # State dimensions
    n_time  = m.shape[0]

    # Original State Shape
    gains_shape = m.shape[1:]

    # Smooth State Vectors
    ms = np.zeros_like(m)

    # Smooth Covariance matrices
    Ps = np.zeros_like(P)
    G_values = np.zeros_like(P)

    # Set Initial Smooth Values
    ms[-1] = m[-1]
    Ps[-1] = P[-1]

    # Run Extended Kalman Smoother with
    # Numpy matrices
    for k in range(-2, -(n_time + 1), -1):   

        # Predict Step
        mp = gains_vector(m[k])
        Pt = P[k].astype(np.complex128)
        Pp = Pt + Q

        # Smooth Step
        Pinv = np.diag(1.0/np.diag(Pp))
        G = Pt @ Pinv

        # Record Posterior Smooth Values
        e = gains_vector(ms[k + 1]) - mp
        E = (Ps[k + 1] - Pp).astype(np.complex128)
        ms[k] = gains_reshape(mp + G @ e, gains_shape)
        Ps[k] = np.diag(np.diag(Pt + G @ E @ G.T).real)

        G_values[k] = G.real

    # Return Posterior smooth states and covariances
    return ms, Ps, G_values