import numpy as np


def phase_gains(lm, freq, n_time, n_ant, alpha_std):
    """Produce phase-only (screen) gains based on dimensions parsed in."""

    # Extract dimensions
    n_dir = lm.shape[0]
    n_freq = freq.size

    # Create basis matrix for plane [1, l, m]
    n_coeff = 3
    l_coord = lm[:, 0]
    m_coord = lm[:, 1]
    basis = np.hstack((np.ones((n_dir, 1), 
        dtype=np.float64), l_coord[:, None], m_coord[:, None]))

    # Get coeffs
    alphas = alpha_std * np.random.randn(n_time, n_ant, n_coeff, 2)

    # Normalise frequencies
    freq_norm = freq/freq.min()

    # Simulate phases
    phases = np.zeros((n_time, n_ant, n_freq, n_dir, 2),
                      dtype=np.complex64)
    for t in range(n_time):
        for p in range(n_ant):
            for c in [0, 1]:
                # Get screen at source locations
                screen = basis.dot(alphas[t, p, :, c])

                # Apply frequency scaling
                phases[t, p, :, :, c] = screen[None, :]/freq_norm[:, None]

    # Return phase-form gains
    return np.exp(1.0j*phases)