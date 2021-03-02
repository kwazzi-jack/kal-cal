from tests.conftest import DECIMALS
import numpy as np
import pytest


# ~~!~~ TESTS ~~!~~

def test_meas_equation_coo(clean_meas_vec, jac_coo, true_state_vec):    

    LHS = np.round(clean_meas_vec, DECIMALS)
    RHS = np.round((jac_coo @ true_state_vec), DECIMALS)
    
    assert not (LHS != RHS).all()


def test_meas_equation_csr(clean_meas_vec, jac_csr, true_state_vec):    
    
    LHS = np.round(clean_meas_vec, DECIMALS)
    RHS = np.round((jac_csr @ true_state_vec), DECIMALS)
    
    assert not (LHS != RHS).all()


def test_meas_equation_np(clean_meas_vec, jac_np, true_state_vec):    
    
    LHS = np.round(clean_meas_vec, DECIMALS)
    RHS = np.round((jac_np @ true_state_vec), DECIMALS)
    
    assert not (LHS != RHS).all()