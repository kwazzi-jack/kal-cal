import numpy as np
from scipy import sparse
from numba import njit, prange


@njit(parallel=True, fastmath=True, nogil=True)
def _construct_coo_lists(
    model : np.ndarray, 
    weight : np.ndarray, 
    jones : np.ndarray,
    antenna1 : np.ndarray, 
    antenna2 : np.ndarray
    ):

    # Dimension 
    n_ant, n_chan, n_dir = jones.shape
    n_row = model.shape[0]
    n_terms = n_chan * n_dir * n_ant * (n_ant - 1)

    # COO lists
    rows = np.zeros(n_terms, dtype=np.int32)
    cols = np.zeros(n_terms, dtype=np.int32)
    data = np.zeros(n_terms, dtype=np.complex128)

    # Populate lists
    for s in prange(n_dir):
        for nu in prange(n_chan):
            for row in prange(n_row):

                # Antenna pairings
                p = antenna1[row]
                q = antenna2[row]

                # Square-root of weight
                sqrtW = np.sqrt(weight[row])

                # Term index
                n = 2 * (s + n_dir * nu + n_dir * n_chan * row)

                # Row Indices
                rows[n] = 2 * n_row * nu + row
                rows[n + 1] = rows[n] + n_row

                # Column Indices
                cols[n] = n_ant * n_dir * nu + n_ant * s + p
                cols[n + 1] = n_ant * n_dir * nu + n_ant * s + q
                
                # Data-values
                data[n] = sqrtW * model[row, nu, s]\
                            * jones[q, nu, s].conjugate()
                data[n + 1] = sqrtW * model[row, nu, s].conjugate()\
                            * jones[p, nu, s].conjugate()                            
      
    return data, rows, cols


def _build_coo_matrix(*args):
    data, rows, cols = _construct_coo_lists(*args[1:])
    return sparse.coo_matrix((data, (rows, cols)), 
                                shape=args[0], 
                                dtype=np.complex64)


def compute_aug_coo(
    model : np.ndarray, 
    weight : np.ndarray, 
    aug_jones : np.ndarray,
    antenna1 : np.ndarray, 
    antenna2 : np.ndarray    
    ):

    # Dimensions
    n_ant, n_chan, n_dir, _ = aug_jones.shape

    # Normal Jacobian shape
    jac_shape = (n_chan * n_ant * (n_ant - 1),
                    n_chan * n_dir * n_ant)
    
    J_lhs = _build_coo_matrix(jac_shape, model, weight, 
                aug_jones[:, :, :, 0], antenna1, antenna2)

    J_rhs = _build_coo_matrix(jac_shape, model, weight, 
                aug_jones[:, :, :, 1], antenna2, antenna1)

    # Horizontal stack halves
    J = 1/2*sparse.hstack((J_lhs, J_rhs))

    # Return jacobian
    return J.astype(np.complex128)
    


def compute_aug_csr(
    model : np.ndarray, 
    weight : np.ndarray, 
    aug_jones : np.ndarray,
    antenna1 : np.ndarray, 
    antenna2 : np.ndarray    
    ):
    
    return compute_aug_coo(model, weight, aug_jones, 
            antenna1, antenna2).tocsr().astype(np.complex128)


@njit(parallel=True, fastmath=True, nogil=True)
def _build_np_matrix(
    model : np.ndarray, 
    weight : np.ndarray, 
    jones : np.ndarray,
    antenna1 : np.ndarray, 
    antenna2 : np.ndarray
    ):

    # Dimension 
    n_ant, n_chan, n_dir = jones.shape
    n_row = model.shape[0]
    jac_shape = (n_chan * n_ant * (n_ant - 1),
                    n_chan * n_dir * n_ant)

    # Empty Jacobian
    jacobian = np.zeros(jac_shape, dtype=np.complex128)

    # Populate lists
    for s in prange(n_dir):
        for nu in prange(n_chan):
            for row in prange(n_row):

                # Antenna pairings
                p = antenna1[row]
                q = antenna2[row]

                # Square-root of weight
                sqrtW = np.sqrt(weight[row])

                # Row Indices
                r1 = 2 * n_row * nu + row
                r2 = r1 + n_row

                # Column Indices
                c1 = n_ant * n_dir * nu + n_ant * s + p
                c2 = n_ant * n_dir * nu + n_ant * s + q
                
                # Data-values
                jacobian[r1, c1] = sqrtW * model[row, nu, s]\
                                    * jones[q, nu, s].conjugate()
                jacobian[r2, c2] = sqrtW * model[row, nu, s].conjugate()\
                                    * jones[p, nu, s].conjugate()

    return jacobian


@njit(fastmath=True, nogil=True)
def compute_aug_np(
    model : np.ndarray, 
    weight : np.ndarray, 
    aug_jones : np.ndarray,
    antenna1 : np.ndarray, 
    antenna2 : np.ndarray    
    ):

    # Build left and right half of
    # augmented jacobian matrix
    
    J_lhs = _build_np_matrix(model, weight, aug_jones[:, :, :, 0], 
                                antenna1, antenna2)

    J_rhs = _build_np_matrix(model, weight, aug_jones[:, :, :, 1], 
                                antenna2, antenna1)

    # Horizontal stack halves
    J = 1/2*np.hstack((J_lhs, J_rhs))

    # Return jacobian
    return J