import numpy as np
import pytest

from kalcal.tools.jacobian import (compute_aug_coo, 
    compute_aug_csr, compute_aug_np)


@pytest.fixture(scope='module')
def jac_coo(time_choice, load_data):
    tbin_indices, tbin_counts, ant1, ant2,\
            _, model, weight, jones = load_data

    k = time_choice

    # Slice indices
    start = tbin_indices[k]
    end = start + tbin_counts[k]
    
    # Calculate Slices
    row_slice = slice(start, end)
    model_slice = model[row_slice]
    weight_slice = weight[row_slice]
    ant1_slice = ant1[row_slice]
    ant2_slice = ant2[row_slice]
    jones_slice = jones[k] 

    return compute_aug_coo(model_slice, weight_slice, 
        jones_slice, ant1_slice, ant2_slice)


@pytest.fixture(scope='module')
def jac_csr(time_choice, load_data):
    tbin_indices, tbin_counts, ant1, ant2,\
            _, model, weight, jones = load_data

    k = time_choice

    # Slice indices
    start = tbin_indices[k]
    end = start + tbin_counts[k]
    
    # Calculate Slices
    row_slice = slice(start, end)
    model_slice = model[row_slice]
    weight_slice = weight[row_slice]
    ant1_slice = ant1[row_slice]
    ant2_slice = ant2[row_slice]
    jones_slice = jones[k] 

    return compute_aug_csr(model_slice, weight_slice, 
        jones_slice, ant1_slice, ant2_slice)


@pytest.fixture(scope='module')
def jac_np(time_choice, load_data):
    tbin_indices, tbin_counts, ant1, ant2,\
            _, model, weight, jones = load_data

    k = time_choice

    # Slice indices
    start = tbin_indices[k]
    end = start + tbin_counts[k]
    
    # Calculate Slices
    row_slice = slice(start, end)
    model_slice = model[row_slice]
    weight_slice = weight[row_slice]
    ant1_slice = ant1[row_slice]
    ant2_slice = ant2[row_slice]
    jones_slice = jones[k] 

    return compute_aug_np(model_slice, weight_slice, 
        jones_slice, ant1_slice, ant2_slice)


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