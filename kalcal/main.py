import matplotlib.pyplot as plt
import numpy as np
from filters import ekf, iekf, enkf
from smoothers import eks
from tools.utils import gains_reshape, gains_vector
from generation import parser
from generation import generate
from generation.create_ms import create_ms
from generation import cleaner, loader
from plotting.multiplot import plot_time
import matplotlib.pyplot as plt
import packratt


def main():   

    # Get ms via packratt
    packratt.get('/MSC_DATA/MS/KAT7_200_7_1.tar.gz', 'datasets/ms/')

    # Get configurations from yaml
    yaml_args = parser.yaml_parser('config.yml')
    ms_args = yaml_args['create_ms']
    gen_args = yaml_args['generate']    

    # Create measurement set
    #create_ms(ms_args)

    # Create jones & model data
    gen_args.ms = 'datasets/ms/KAT7_200_7_1.MS'
    gen_args.out = 'datasets/gains/normal.npy'    
    
    # Generate jones and data
    generate.both(gen_args)

    tbin_indices, tbin_counts, ant1, ant2,\
            vis, model, weight, jones = loader.get_data(gen_args)    

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