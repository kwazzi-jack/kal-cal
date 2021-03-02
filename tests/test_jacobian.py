import numpy as np
import pytest


# ~~!~~ TESTS ~~!~~

def test_sparse_coo_properties(jac_coo, jac_shape, jac_nnz):    

    assert jac_coo.data.dtype == np.complex128
    assert jac_coo.shape == jac_shape
    assert jac_coo.nnz == jac_nnz


def test_sparse_csr_properties(jac_csr, jac_shape, jac_nnz):    

    assert jac_csr.data.dtype == np.complex128
    assert jac_csr.shape == jac_shape
    assert jac_csr.nnz == jac_nnz


def test_numpy_properties(jac_np, jac_shape):    

    assert jac_np.dtype == np.complex128
    assert jac_np.shape == jac_shape