import numpy as np


def gains_magnitude_time(jones, index, ref):

    if jones.ndim == 5:
        n, c, d = index 
        return jones[:, ref, c, d, 0]\
            * jones[:, n, c, d, 0].conj().T

    elif jones.ndim == 4:
        n, c, d = index 
        return jones[:, ref, c, d]\
            * jones[:, n, c, d].conj().T


def gains_magnitude_freq(jones, index, ref):

    if jones.ndim == 5:
        t, n, d = index 
        return jones[t, ref, :, d, 0]\
            * jones[t, n, :, d, 0].conj().T

    elif jones.ndim == 4:
        t, n, d = index 
        return jones[t, ref, :, d]\
            * jones[t, n, :, d].conj().T