import numpy as np

from kalcal.tools.utils import gains_vector


def new_P0(m0, ms0, Ps0, alpha=1.0):
    """TODO DOC STRING"""

    print("==> Tuning P0")
    # Calculate diagonal of P0 - considering only the diagonal
    # and real values
    P0_diag = np.diag(Ps0 + (gains_vector((ms0 - m0))\
        @ gains_vector((ms0 - m0)).conj().T).real)
                 
    # Return full matrix of P0 with alpha component
    return alpha * np.diag(P0_diag)


def new_Q(T, ms, Ps, G):
    """TODO DOC STRING"""

    print("==> Tuning Q")
    SIGMA = np.zeros_like(Ps[0], dtype=np.complex128)
    PHI = np.zeros_like(Ps[0], dtype=np.complex128)
    C = np.zeros_like(Ps[0], dtype=np.complex128)
    shape = (Ps[0].shape[0], 1)
    
    for k in range(1, T + 1):
        m1 = gains_vector(ms[k]).reshape(shape)
        m2 = gains_vector(ms[k - 1]).reshape(shape)

        SIGMA += Ps[k] + m1 @ m1.conj().T
        PHI += Ps[k - 1] + m2 @ m2.conj().T
        C += Ps[k] @ G[k - 1].conj().T + m1 @ m2.conj().T

    SIGMA *= 1/T
    PHI *= 1/T
    C *= 1/T

    # Diagonal real-values
    Q_diag = np.diag(SIGMA - C - C.conj().T + PHI).real

    # Return new Q
    return np.diag(Q_diag).real