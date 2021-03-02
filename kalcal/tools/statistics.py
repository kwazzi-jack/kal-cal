import numpy as np


def sigma_test(states, true_jones, cov, n):
    
    n_time, n_ant, n_chan, n_dir = true_jones.shape 
    aug_true_jones = np.stack((true_jones, 
                            true_jones.conj()), axis=4)
    stats = np.zeros(n_time)
    m = 2 * n_ant * n_chan * n_dir
    
    for t in range(n_time):
        x = states[t].ravel()
        std = np.sqrt(np.diag(cov[t]))
        mu = aug_true_jones[t].ravel()

        LB = x - n * std
        UB = x + n * std
        
        stats[t] = 1/m * np.sum((LB <= mu) & (mu <= UB))
        
    return 1/n_time * np.sum(stats)