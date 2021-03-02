import numpy as np
from numba import jit, prange


@jit(nopython=True, parallel=False,
        fastmath=True, nogil=True)
def _csr_dot_vec_fn(
    A_data, 
    A_indices, 
    A_indptr, 
    A_rows, 
    A_dtype,
    x):

    Ax = np.zeros(A_rows, dtype=A_dtype)

    for i in range(A_rows):
        Ax_i = 0.0
        for dataIdx in range(A_indptr[i], A_indptr[i + 1]):
            j = A_indices[dataIdx]
            Ax_i += A_data[dataIdx] * x[j]
        
        Ax[i] = Ax_i

    return Ax 


def csr_dot_vec(A, x):
    A_data = A.data
    A_indices = A.indices
    A_indptr = A.indptr
    A_rows = A.shape[0] 
    A_dtype = A.dtype    

    return _csr_dot_vec_fn(A_data, 
                           A_indices,
                           A_indptr, 
                           A_rows,
                           A_dtype, 
                           x)