from kalcal.filters import ekf, iekf
from kalcal.smoothers import eks
from kalcal.tools.utils import gains_vector
from kalcal.generation import parser
from kalcal.generation import from_ms
from kalcal.generation import create_ms
from kalcal.generation import loader
from kalcal.plotting.multiplot import plot_time
from kalcal.tools.statistics import (cond_number, state_sigma_test,
    magnitude_sigma_test, cond_number)

import matplotlib.pyplot as plt
import numpy as np
from os import path
from tabulate import tabulate


def main():   
    # Get configurations from yaml
    yaml_args = parser.yaml_parser('config.yml')
    cms_args = yaml_args['create_ms']
    fms_args = yaml_args['from_ms'] 
    
    # Create measurement set
    if path.isdir(cms_args.msname):
        s = input(f"==> `{cms_args.msname}` exists, "\
                + "continue with `create_ms`? (y/n) ")
        
        if s == 'y':
            create_ms.new(cms_args) 
    else:
        create_ms.new(cms_args)  
    
    # Generate jones and data
    if path.isfile(fms_args.out):
        s = input(f"==> `{fms_args.out}` exists, "\
                + "continue with `from_ms`? (y/n) ")
        
        if s == 'y':
            from_ms.both(fms_args) 
    else:
        from_ms.both(fms_args) 

    # Load ms and gains data
    tbin_indices, tbin_counts, ant1, ant2,\
            vis, model, weight, jones = loader.get(fms_args)    

    #Get dimension values
    n_time, n_ant, n_chan, n_dir = jones.shape    
    
    # Choose parameters for Q and R
    sigma_f = 0.1
    sigma_n = 0.1

    print(f"==> Selected: sigma_f = {sigma_f:.3f}, sigma_n = {sigma_n:.3f}")

    # Choose kalman filter and smoother
    ext_kalman_filter = ekf.sparse_algorithm
    ext_kalman_filter_2 = ekf.numpy_algorithm
    ext_kalman_smoother = eks.numpy_algorithm

    # Set random seed
    np.random.seed(666)

    # Prior state and covariance
    mp = np.ones((n_ant, n_chan, n_dir, 2), dtype=np.complex128)
    mp = gains_vector(mp)      
    Pp = np.eye(mp.size, dtype=np.complex128)

    # Process and measurement noise
    Q = sigma_f**2 * np.eye(mp.size, dtype=np.complex128)
    R = 2*sigma_n**2 * np.eye(n_ant * (n_ant - 1) * n_chan, dtype=np.complex128) 
    
    # Run kalman filter
    m, P = ext_kalman_filter(mp, Pp, model, vis, weight, Q, R, 
                                ant1, ant2, tbin_indices, tbin_counts)

    m2, P2 = ext_kalman_filter_2(mp, Pp, model, vis, weight, Q, R, 
                                ant1, ant2, tbin_indices, tbin_counts)
    # Run kalman smoother
    ms, Ps, G = ext_kalman_smoother(m, P, Q)
    ms2, Ps2, G = ext_kalman_smoother(m2, P2, Q)
    
    # Sigma-test on States (g_p)
    m = ms2
    P = Ps2
    n_states = 2 * n_time * n_ant * n_chan * n_dir
    SF1 = np.mean(state_sigma_test(m, jones, P, 1))*100
    SS1 = np.mean(state_sigma_test(ms, jones, Ps, 1))*100
    SF2 = np.mean(state_sigma_test(m, jones, P, 2))*100
    SS2 = np.mean(state_sigma_test(ms, jones, Ps, 2))*100
    SF3 = np.mean(state_sigma_test(m, jones, P, 3))*100
    SS3 = np.mean(state_sigma_test(ms, jones, Ps, 3))*100

    S1 = ['1', f"{SF1:.2f}%", f"{SS1:.2f}%", n_states]        
    S2 = ['2', f"{SF2:.2f}%", f"{SS2:.2f}%", n_states]
    S3 = ['3', f"{SF3:.2f}%", f"{SS3:.2f}%", n_states]
    S = [S1, S2, S3]

    print("==> State Sigma-tests:")
    print(tabulate(S, headers=['Sigmas', 'Filter', 'Smoother', 'States'], 
                    tablefmt='fancy_grid'))

    # Sigma-test on Magnitudes (g_p x g_q^*)
    MF1 = np.mean(magnitude_sigma_test(m, jones, P, 1))*100
    MS1 = np.mean(magnitude_sigma_test(ms, jones, Ps, 1))*100
    MF2 = np.mean(magnitude_sigma_test(m, jones, P, 2))*100
    MS2 = np.mean(magnitude_sigma_test(ms, jones, Ps, 2))*100
    MF3 = np.mean(magnitude_sigma_test(m, jones, P, 3))*100
    MS3 = np.mean(magnitude_sigma_test(ms, jones, Ps, 3))*100

    M1 = ['1', f"{MF1:.2f}%", f"{MS1:.2f}%", n_states]
    M2 = ['2', f"{MF2:.2f}%", f"{MS2:.2f}%", n_states]
    M3 = ['3', f"{MF3:.2f}%", f"{MS3:.2f}%", n_states]
    M = [M1, M2, M3]

    print("==> Magnitude Sigma-tests:")
    print(tabulate(M, headers=['Sigmas', 'Filter', 'Smoother', 'States'], 
                    tablefmt='fancy_grid'))

    print(cond_number(P))
    print(cond_number(Ps))
    # Plot magnitudes of antenna 1 to 3
    show = [1, 2, 3]
    plot_time(
        jones, 'True Jones', '-',
        ms, 'EKF - SPARSE', '-',
        ms2, 'EKF - NUMPY', '-',
        title='NUMPY Algorithms',
        show=show
    )    

    plt.show()


if __name__ == "__main__":
    main()