import numpy as np
from numba import njit, objmode
from kalcal.tools.utils import gains_vector, gains_reshape


@njit(fastmath=True, nogil=True)
def numpy_algorithm(
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
    head = "==> Extended Kalman Smoother (NUMPY|JIT): "
    for k in range(-2, -(n_time + 1), -1):   
         
        # Progress Bar in object-mode
        with objmode():
            bar_len = 100
            total = n_time - 1
            filled_len = int(round(bar_len*(-k - 1)/float(n_time - 1)))
            bar = u"\u2588" * filled_len + ' '\
                    * (bar_len - filled_len)
            print("\r%s%d%%|%s| %d/%d" % (head, (-k - 1)/total*100, 
                                            bar, -k - 1, total), end="")

        # Predict Step
        mp = gains_vector(m[k])
        Pt = P[k].astype(np.complex128)
        Pp = Pt + Q

        # Smooth Step
        Pinv = np.linalg.inv(Pp).astype(np.complex128)
        G = Pt @ Pinv

        # Record Posterior Smooth Values
        e = gains_vector(ms[k + 1]) - mp
        E = (Ps[k + 1] - Pp).astype(np.complex128)
        ms[k] = gains_reshape(mp + G @ e, gains_shape)
        Ps[k] = np.diag(np.diag(Pt + G @ E @ G.T).real)

        G_values[k] = G.real

    # Newline
    print()

    # Return Posterior smooth states and covariances
    return ms, Ps, G_values