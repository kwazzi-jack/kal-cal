from omegaconf import OmegaConf as ocf
from kalcal.filters import ekf
from kalcal.smoothers import eks
from kalcal.tools.utils import gains_vector
from daskms import xds_from_ms
import numpy as np
from time import time


def calibrate(ms, **kwargs):
    """A vanilla calibrate command to use the kalman
    filter and smoother in an ordinary manner."""

    # Options to attributed dictionary
    if kwargs["yaml"] is not None:
        options = ocf.load(kwargs["yaml"])
    else:    
        options = ocf.create(kwargs)    

    # Set to struct
    ocf.set_struct(options, True)

    # Choose filter algorithm
    kalman_filter = {
        "numba" : ekf.numba_algorithm,
        "sparse" : ekf.sparse_algorithm
    }[options.algorithm.lower()]
    
    # Choose smoother algorithm
    kalman_smoother = eks.numba_algorithm

    # Load ms
    MS = xds_from_ms(ms)[0]

    # Get dimensions (correlations need to be adapted)
    dims = ocf.create(dict(MS.sizes))
    n_row = dims.row
    n_chan = dims.chan
    n_corr = dims.corr

    # Load model visibilities (dask ignored for now)
    model = MS.get(options.model_column).data.reshape(
        n_row, n_chan, -1, n_corr).compute().astype(np.complex128)

    # Get number of directions from model visibilities column
    n_dir = model.shape[2]

    # Load data visibilities (dask ignored for now)
    vis = MS.get(options.vis_column).data.compute().astype(np.complex128)

    # Load weights (dask ignored for now)
    weight = MS.get(options.weight_column).data.compute().astype(np.complex128)

    # Get time-bin indices and counts
    _, tbin_indices, tbin_counts = np.unique(MS.TIME,
                                        return_index=True, 
                                        return_counts=True)   

    # Get antenna arrays (dask ignored for now)
    ant1 = MS.ANTENNA1.data.compute()
    ant2 = MS.ANTENNA2.data.compute()

    # Set antenna dimension
    n_ant = np.max((np.max(ant1), np.max(ant2))) + 1

    # Adjust for correlations axis (4 to 1)
    model = model[:, :, :, 0]
    vis = vis[:, :, 0]
    weight = weight[:, 0]

    # Create priors
    mp = np.ones((n_ant, n_chan, n_dir, 2), dtype=np.complex128)
    mp = gains_vector(mp)
    Pp = np.eye(mp.size, dtype=np.complex128)

    # Create noise matrices
    Q = options.sigma_f**2 * np.eye(mp.size, dtype=np.complex128)
    R = 2 * options.sigma_n**2\
        * np.eye(n_ant * (n_ant - 1) * n_chan, dtype=np.complex128) 

    # Variable to keep track of algorithm direction
    a_dir = "forward"

    # Run Kalman Filter for requested number of times
    total_start = filter_start = time()
    for i in range(options.filter):
        m, P = kalman_filter(mp, Pp, model, vis, weight, Q, R, 
                                ant1, ant2, tbin_indices, tbin_counts)        

        # Correct flipping if last iteration
        if i == options.filter - 1:
            if a_dir == "backward":
                # Reset algorithm direction
                a_dir = "forward"

                # Flip arrays
                m = m[::-1]
                P = P[::-1]
                model = model[::-1]
                vis = vis[::-1]
                weight = weight[::-1]
                tbin_indices = tbin_indices[::-1] # For consistency
                tbin_counts = tbin_counts[::-1] # For consistency
        else:
            # Set algorithm direction
            if a_dir == "forward":
                a_dir == "backward"
            elif a_dir == "backward":
                a_dir == "forward"
            
            # Flip arrays
            mp = gains_vector(m[-1])
            Pp = P[-1]
            model = model[::-1]
            vis = vis[::-1]
            weight = weight[::-1]
            tbin_indices = tbin_indices[::-1] # For consistency
            tbin_counts = tbin_counts[::-1] # For consistency
    
    # Stop filter timer and start smoother timer
    smoother_start = time()
    filter_time = smoother_start - filter_start

    # Run Kalman Smoother for requested number of times
    for i in range(options.smoother):
        ms, Ps, _ = kalman_smoother(m, P, Q)        

        # Correct flipping if last iteration
        if i == options.smoother - 1:
            if a_dir == "backward":
                # Reset algorithm direction
                a_dir = "forward"

                # Flip arrays
                ms = ms[::-1]
                Ps = Ps[::-1]
        else:
            # Set algorithm direction
            if a_dir == "forward":
                a_dir == "backward"
            elif a_dir == "backward":
                a_dir == "forward"
            
            # Flip arrays
            m = ms[::-1]
            P = Ps[::-1]

    # Stop time
    stop_time = time()
    total_time = stop_time - total_start
    smoother_time = stop_time - smoother_start

    # Output to wanted gains to npy file
    if options.which_gains.lower() == "smoother":
        gains_file = "smoother_" + options.out_file
        with open(gains_file, 'wb') as file:            
                np.save(file, ms)        
    elif options.which_gains.lower() == "filter":
        gains_file = "filter_" + options.out_file,
        with open(gains_file, 'wb') as file:            
                np.save(file, m)
    elif options.which_gains.lower() == "both":
        gains_file = options.out_file
        with open(gains_file, 'wb') as file:            
                np.save(file, m)
                np.save(file, ms)

    # Show timer results
    print(f"==> Completed and gains saved to: {gains_file}")
    print(f"==> Filter run(s): {options.filter} "\
          + f"in {np.round(filter_time, 3)} s, "\
          + f"Smoother run(s): {options.smoother} "\
          + f"in {np.round(smoother_time, 3)} s, "\
          + f"Total taken: {np.round(total_time, 3)} s")