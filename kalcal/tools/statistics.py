import numpy as np
from kalcal.tools.utils import diag_cov_reshape
    

def state_sigma_test(states, true_jones, cov, n=1):
    
    n_time, n_ant, n_chan, n_dir = true_jones.shape 

    aug_true_jones = np.stack((true_jones, 
                            true_jones.conj()), axis=4)

    stats = np.zeros_like(states, dtype=np.int16)
    shape = (n_ant, n_chan, n_dir, 2)
    for t in range(n_time):        
        std = np.sqrt(diag_cov_reshape(cov[t], shape))    

        for a in range(n_ant):
            for c in range(n_chan):
                for s in range(n_dir): 
                    for i in range(2):
                        x = states[t, a, c, s, i]
                        mu = aug_true_jones[t, a, c, s, i]
                        LB = x - n * std[a, c, s, i]
                        UB = x + n * std[a, c, s, i]
                        stats[t, a, c, s, i] =\
                            ((LB <= mu) & (mu <= UB))
        
    return stats


def magnitude_sigma_test(states, true_jones, cov, n=1, ref_ant=0):
    
    n_time, n_ant, n_chan, n_dir = true_jones.shape 

    aug_true_jones = np.stack((true_jones, 
                            true_jones.conj()), axis=4)

    stats = np.zeros_like(states, dtype=np.int16)
    shape = (n_ant, n_chan, n_dir, 2)
    for t in range(n_time):        
        std = np.sqrt(diag_cov_reshape(cov[t], shape))    

        for a in range(n_ant):
            if a == ref_ant:
                continue
            for c in range(n_chan):
                for s in range(n_dir): 
                    for i in range(2):
                        x = states[t, ref_ant, c, s, i]\
                            * states[t, a, c, s, i].conjugate() 
                        mu = aug_true_jones[t, ref_ant, c, s, i]\
                            * aug_true_jones[t, a, c, s, i].conjugate()
                        
                        LB = x - n * std[a, c, s, i]
                        UB = x + n * std[a, c, s, i]
                        stats[t, a, c, s, i] =\
                            ((LB <= mu) & (mu <= UB))
        
    return stats