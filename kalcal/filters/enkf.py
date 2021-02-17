import numpy as np
from numba import jit, objmode
from tools.utils import gains_vector, gains_reshape, measure_vector,\
                        state_ensemble, measure_noise, process_noise
from tools.jacobian import compute_aug_csr, compute_aug_np
from tools.sparseops import csr_dot_vec


def sparse_algorithm(
    mp           : np.ndarray, 
    Pp           : np.ndarray, 
    model        : np.ndarray, 
    vis          : np.ndarray, 
    weight       : np.ndarray, 
    Q            : np.ndarray, 
    R            : np.ndarray, 
    ant1         : np.ndarray, 
    ant2         : np.ndarray, 
    tbin_indices : np.ndarray, 
    tbin_counts  : np.ndarray,
    Nsamples     : np.int32=10): 

    """Sparse-matrix implementation of EnKF algorithm. Not
    numba-compiled."""

    # Time counts
    n_time = len(tbin_indices)

    # Number of Baselines
    n_bl = model.shape[0]//n_time

    # Number of Antennas
    n_ant = int((np.sqrt(8*n_bl + 1) + 1))//2
    
    # Dimensions
    n_chan, n_dir = model.shape[1:]

    # Matrix-size
    axis_length = n_ant * n_chan * n_dir

    # Original matrix size    
    gains_shape = (n_time, n_ant, n_chan, n_dir, 2)

    # Jacobian shape
    shape = gains_shape[1:]

    # Covariance shape
    covs_shape = (n_time, 2*axis_length, 2*axis_length)

    # State vectors
    m = np.zeros(gains_shape, dtype=np.complex128)

    # Covariance matrices
    P = np.zeros(covs_shape, dtype=np.complex128)
    
    # Initial state and covariance
    m[0] = gains_reshape(mp, shape)

    C = Pp.real

    # Select CSR jacobian function 
    aug_jac = compute_aug_csr
    
    # Calculate R^{-1} for a diagonal
    Rinv = np.diag(1.0/np.diag(R))
    
    # Run Extended Kalman Filter with 
    # Sparse matrices
    print("\n Ensemble Kalman Filter (SPARSE):")
    for k in range(1, n_time): 

        # # Progress Bar
        # bar_len = 100
        # total = n_time - 1
        # filled_len = int(round(bar_len*k/float(n_time - 1)))
        # bar = u"\u2588" * filled_len + ' '\
        #         * (bar_len - filled_len)
        # print("\r%d%%|%s| %d/%d" % (k/total*100, 
        #                             bar, k, total), end="")

        q = process_noise(Q)
        
        mp = gains_vector(m[k - 1])
        
        # Ensemble Step
        M = state_ensemble(mp, C) + q 
        
        mi = np.mean(M, axis=1)
        
        # Slice indices
        start = tbin_indices[k - 1]
        end = start + tbin_counts[k - 1]
        
        # Calculate Slices
        row_slice = slice(start, end)
        vis_slice = vis[row_slice]
        model_slice = model[row_slice]
        weight_slice = weight[row_slice]
        ant1_slice = ant1[row_slice]
        ant2_slice = ant2[row_slice]
        jones_slice = gains_reshape(mi, shape)        

        # Calculate Augmented Jacobian
        J = aug_jac(model_slice, weight_slice, 
                        jones_slice, ant1_slice, ant2_slice)
        
        # Hermitian of Jacobian
        J_herm = J.conjugate().T
        
        D = J @ C @ J_herm + R
        K = C @ J_herm @ np.linalg.inv(D)

        # Calculate Measure Vector
        y = measure_vector(vis_slice, weight_slice, 
                            n_ant, n_chan)        
        
        e = measure_noise(R)

        Y = np.zeros((y.shape[0], Nsamples), dtype=np.complex128)
        Mf = np.zeros_like(M)

        for i in range(Nsamples):
            Y[:, i] = y + e[:, i] 
            jones_slice = gains_reshape(M[:, i], shape)

        Mf = M + K @ (Y - J @ M)
        
        mf = np.mean(Mf, axis=1)
        C = np.diag(np.diag(np.cov(Mf))).real
    
        m[k] = gains_reshape(mf, shape)

    # Print newline
    print()

    # Return Posterior states and covariances
    return m