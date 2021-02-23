from kalcal.filters import ekf, iekf, enkf
from kalcal.smoothers import eks
from kalcal.tools.utils import gains_reshape, gains_vector
from kalcal.generation import parser
from kalcal.generation import from_ms
from kalcal.generation import create_ms
from kalcal.generation import loader
from kalcal.plotting.multiplot import plot_time

import matplotlib.pyplot as plt
import numpy as np
from os import path


def main():   
    # Get configurations from yaml
    yaml_args = parser.yaml_parser('config.yml')
    cms_args = yaml_args['create_ms']
    fms_args = yaml_args['from_ms'] 
    
    # Create measurement set
    if path.isdir(cms_args.msname):
        s = input(f"==> {cms_args.msname} exists, "\
                + "continue with `create_ms`? (y/n) ")
        
        if s == 'y':
            create_ms.new(cms_args) 
    else:
        create_ms.new(cms_args)  
    
    # Generate jones and data
    if path.isfile(fms_args.out):
        s = input(f"==> {fms_args.out} exists, "\
                + "continue with `generate`? (y/n) ")
        
        if s == 'y':
            from_ms.both(fms_args) 
    else:
        from_ms.both(fms_args) 

    # Load ms and gains data
    tbin_indices, tbin_counts, ant1, ant2,\
            vis, model, weight, jones = loader.get(fms_args)    

    #Get dimension values
    n_time, n_ant, n_chan, n_dir = jones.shape    
    
    sigma_f = 0.1
    sigma_n = 0.1

    ext_kalman_filter = ekf.numpy_algorithm
    ext_kalman_smoother = eks.numpy_algorithm

    np.random.seed(666)
    mp = np.ones((n_ant, n_chan, n_dir, 2), dtype=np.complex128)
    mp = gains_vector(mp)  

    Pp = np.eye(mp.size, dtype=np.complex128)
    Q = sigma_f**2 * np.eye(mp.size, dtype=np.complex128)
    R = sigma_n**2 * np.eye(n_ant * (n_ant - 1) * n_chan, dtype=np.complex128) 
    
    m, P = ext_kalman_filter(mp, Pp, model, vis, weight, Q, R, 
                                ant1, ant2, tbin_indices, tbin_counts)

    ms, Ps, G = ext_kalman_smoother(m, P, Q)

    show = [1, 2, 3]
    plot_time(
        jones, 'True Jones', '-',
        m, 'EKF - NUMPY', '+',
        ms, 'EKS - NUMPY', '--',
        title='NUMPY Algorithms',
        show=show
    )    

    plt.show()


if __name__ == "__main__":
    main()