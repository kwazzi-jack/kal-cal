import numpy as np
from numba import jit, objmode
from kalcal.tools.utils import gains_vector, gains_reshape, measure_vector
from kalcal.tools.jacobian import compute_aug_csr, compute_aug_np
from kalcal.tools.sparseops import csr_dot_vec


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
    tol          : np.float64=1e-5,
    maxiter      : np.int32=20,
    alpha        : np.float64=0.5): 

    """Sparse-matrix implementation of Iterated-EKF algorithm. Not
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
    P[0] = Pp
    
    # Select CSR jacobian function 
    aug_jac = compute_aug_csr
    
    # Calculate R^{-1} for a diagonal
    Rinv = np.diag(1.0/np.diag(R))

    # Run Iterated Extended Kalman Filter with 
    # Sparse matrices
    head = "==> Iterated Extended Kalman Filter (SPARSE): "
    for k in range(1, n_time): 

        # Progress Bar
        bar_len = 100
        total = n_time - 1
        filled_len = int(round(bar_len*k/float(n_time - 1)))
        bar = u"\u2588" * filled_len + ' '\
                * (bar_len - filled_len)
        print("\r%s%d%%|%s| %d/%d" % (head, k/total*100, 
                                    bar, k, total), end="")

        # Predict Step
        mp = gains_vector(m[k - 1])
        Pp = P[k - 1] + Q 

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

        # Current Iteration jones
        jones_slice = gains_reshape(mp, shape)                   

        # Calculate Augmented Jacobian
        J = aug_jac(model_slice, weight_slice, 
                        jones_slice, ant1_slice, ant2_slice)       

        # Hermitian of Jacobian
        J_herm = J.conjugate().T

        # Calculate Measure Vector
        y = measure_vector(vis_slice, weight_slice, 
                            n_ant, n_chan) 

        # Initial state
        mi = mp.copy()

        # Current state
        mn = mp

        # Inverse of Prior Covariance
        Pinv = np.diag(1.0/np.diag(Pp)) 

        # Iteration counter
        i = 0

        # State Estimation to reduce bias on 
        # estimation
        while i < maxiter: 
            # Calculate Augmented Jacobian
            J = aug_jac(model_slice, weight_slice, 
                            jones_slice, ant1_slice, ant2_slice)           

            # Hermitian of Jacobian
            J_herm = J.conjugate().T
            
            # Update Step
            v = y - csr_dot_vec(J, mi)                 
            Tinv = np.linalg.inv(Pinv + J_herm @ Rinv @ J)
            Sinv = Rinv - Rinv @ J @ Tinv @ J_herm @ Rinv
            K = Pp @ J_herm @ Sinv

            # Next state update
            mt = mn + alpha*(mi - mn + K @ v)            

            # Stop if tolerance reached
            if np.mean(np.abs(mt - mn)) <= tol:
                break
            
            # Else iterate next step
            i += 1
            mn = mt

            # Next Iteration jones           
            jones_slice = gains_reshape(mn, shape)  

        # Record Posterior values from last iterated state
        m[k] = gains_reshape(mt, shape)
        P[k] = np.diag(np.diag(Pp - K @ J @ Pp).real)

    # Newline
    print()

    # Return Posterior states and covariances
    return m, P


@jit(nopython=True, fastmath=True)
def numpy_algorithm(
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
    tol          : np.float64=1e-5,
    maxiter      : np.int32=20,
    alpha        : np.float64=0.5):  

    """Numpy-matrix implementation of Iterated-EKF algorithm. It is
    numba-compiled."""

    # Time counts
    n_time = len(tbin_indices)

    # Number of Baselines
    n_bl = model.shape[0]//n_time

    # Number of Antennas
    n_ant = int((np.sqrt(8*n_bl + 1) + 1)/2)

    # Dimensions
    n_chan, n_dir = model.shape[1], model.shape[2]

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
    P[0] = Pp
    
    # Select CSR jacobian function 
    aug_jac = compute_aug_np
    
    # Calculate R^{-1} for a diagonal
    Rinv = np.diag(1.0/np.diag(R))
    
    # Run Extended Kalman Filter with 
    # Sparse matrices
    head = "==> Iterated Extended Kalman Filter (NUMPY|JIT): "
    for k in range(1, n_time): 
        
        # Progress Bar in object-mode
        with objmode():
            bar_len = 100
            total = n_time - 1
            filled_len = int(round(bar_len*k/float(n_time - 1)))
            bar = u"\u2588" * filled_len + ' '\
                    * (bar_len - filled_len)
            print("\r%s%d%%|%s| %d/%d" % (head, k/total*100, 
                                        bar, k, total), end="")
        
        # Predict Step
        mp = gains_vector(m[k - 1])
        Pp = P[k - 1] + Q

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

        # Current Iteration jones
        jones_slice = gains_reshape(mp, shape)       

        # Calculate Augmented Jacobian
        J = aug_jac(model_slice, weight_slice, 
                        jones_slice, ant1_slice, ant2_slice)

        # Hermitian of Jacobian
        J_herm = J.conjugate().T

        # Calculate Measure Vector
        y = measure_vector(vis_slice, weight_slice, 
                            n_ant, n_chan)

         # Initial state
        mi = mp.copy()

        # Current state
        mn = mp

        # Inverse of Prior Covariance
        Pinv = np.diag(1.0/np.diag(Pp)) 

        # Iteration counter
        i = 0

        # State Estimation to reduce bias on 
        # estimation
        while i < maxiter:
            # Calculate Augmented Jacobian
            J = aug_jac(model_slice, weight_slice, 
                            jones_slice, ant1_slice, ant2_slice)           

            # Hermitian of Jacobian
            J_herm = J.conjugate().T
            
            # Update Step
            v = y - J @ mi  
            Tinv = np.linalg.inv(Pinv + J_herm @ Rinv @ J)
            Sinv = Rinv - Rinv @ J @ Tinv @ J_herm @ Rinv
            K = Pp @ J_herm @ Sinv

            # Next state update
            mt = mn + alpha*(mi - mn + K @ v)            

            # Stop if tolerance reached
            if np.mean(np.abs(mt - mn)) <= tol:
                break
            
            # Else iterate next step
            i += 1
            mn = mt

            # Next Iteration jones           
            jones_slice = gains_reshape(mn, shape)

        # Record Posterior values
        m[k] = gains_reshape(mt, shape)
        P[k] = np.diag(np.diag(Pp - K @ J @ Pp).real)

    # Newline
    print()

    # Return Posterior states and covariances
    return m, P