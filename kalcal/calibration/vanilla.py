from omegaconf import OmegaConf as ocf
from kalcal.filters import ekf
from kalcal.smoothers import eks
from kalcal.tools.utils import gains_vector, concat_dir_axis
from dask import array as da 
from dask.diagnostics import ProgressBar
from daskms import xds_from_ms, xds_to_table
from africanus.calibration.utils import correct_vis
import numpy as np
from time import time


def calibrate(msname, **kwargs):
    """A vanilla calibrate command to use the kalman
    filter and smoother in an ordinary manner with an ms."""

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
    MS = xds_from_ms(msname)[0]

    # Get dimensions (correlations need to be adapted)
    dims = ocf.create(dict(MS.sizes))
    n_row = dims.row
    n_chan = dims.chan
    n_corr = dims.corr
    
    # Check if single or multiple model columns
    model_columns = options.model_column.replace(" ", "").split(",")    

    # Load model visibilities (dask ignored for now)
    model = concat_dir_axis(MS, model_columns).compute().astype(np.complex128)

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

    # Get flag column
    flag = MS.FLAG.data.compute()

    # Set time dimension
    n_time = len(tbin_indices)

    # Sample a row + chan + dir from model
    s_row = np.random.randint(0, n_row)
    s_chan = np.random.randint(0, n_chan)
    s_dir = np.random.randint(0, n_dir)
    s_model = model[s_row, s_chan, s_dir]

    # Check correlation axis size
    if s_model.shape[0] != 4:
        raise NotImplementedError("Only uses (4,) correlation shape.")

    # Find mode to use
    if s_model.all():
        # All correlations
        mode = "FULL"
        corr = [0, 1, 2, 3]
        
    elif s_model[[0, 3]].all():
        # First and last correlations
        mode = "DIAG"
        corr = [0, 3]

    elif s_model[0]:
        # No correlations
        mode = "NONE"
        corr = [0]

    else:
        # (2 x 2) not implemented yet
        raise ValueError("Cannot identify correlation shape.")
    
    # Gains solutions (@Landman: Have to do this to get around 
    # correct_vis fn as it does a complex division by zero from
    # gains correlations equal to zero, i.e. off-diagonals)
    filter_gains = np.ones((n_time, n_ant, n_chan, n_dir, n_corr, 2),
                                dtype=np.complex128)

    smooth_gains = np.ones((n_time, n_ant, n_chan, n_dir, n_corr, 2),
                                dtype=np.complex128)

    # Run algorithm on each correlation independently
    print(f"==> Correlation Mode: {mode}")
    for i, c in enumerate(corr):
        print(f"==> Running corr={c} ({i + 1}/{len(corr)})")

        # Get data related to correlation
        cmodel = model[..., c]
        cvis = vis[..., c]
        cweight = weight[..., c]

        # Create priors
        mp = np.ones((n_ant, n_chan, n_dir, 2), dtype=np.complex128)
        mp = gains_vector(mp)
        Pp = np.eye(mp.size, dtype=np.complex128)

        # Create noise matrices
        if options.sigma_n is None:
            # Temporary fix till weights are adjusted
            options.sigma_n = 1 

        Q = options.sigma_f**2 * np.eye(mp.size, dtype=np.complex128)
        R = 2 * options.sigma_n**2\
            * np.eye(n_ant * (n_ant - 1) * n_chan, dtype=np.complex128) 

        # Variable to keep track of algorithm direction
        a_dir = "forward"

        # Run Kalman Filter for requested number of times
        total_start = filter_start = time()

        for i in range(options.filter):
            m, P = kalman_filter(mp, Pp, cmodel, cvis, cweight, Q, R, 
                                    ant1, ant2, tbin_indices, 
                                    tbin_counts, options.step_control)        

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
                    a_dir = "backward"
                elif a_dir == "backward":
                    a_dir = "forward"
                
                # Flip arrays
                mp = gains_vector(m[-1])
                Pp = P[-1]
                model = model[::-1]
                vis = vis[::-1]
                weight = weight[::-1]
                tbin_indices = tbin_indices[::-1] # For consistency
                tbin_counts   

        # Save filter gains
        filter_gains[..., c, :] = m.copy()

        # Stop filter timer and start smoother timer
        filter_time = time() - filter_start
        smoother_start = time()

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
                    a_dir = "backward"
                elif a_dir == "backward":
                    a_dir = "forward"
                
                # Flip arrays
                m = ms[::-1]
                P = Ps[::-1]

        # Save smoother gains
        smooth_gains[..., c, :] = ms.copy()

        # Stop time
        stop_time = time()
        total_time = stop_time - total_start
        smoother_time = stop_time - smoother_start        

        # Show timer results
        print(f"==> {options.filter} filter run(s) "\
            + f"in {np.round(filter_time, 3)} s, "\
            + f"{options.smoother} smoother run(s) "\
            + f"in {np.round(smoother_time, 3)} s, "\
            + f"total taken: {np.round(total_time, 3)} s")

    print("==> Calibration complete.")

    # Correct Visibilties
    corrected_data = correct_vis(
        tbin_indices,
        tbin_counts,
        ant1,
        ant2,
        smooth_gains[..., 0],
        vis,
        flag
    ).reshape((n_row, n_chan, n_corr))
    
    # To dask
    corrected_data = da.from_array(corrected_data)

    # Assign and write to ms
    MS = MS.assign(**{options.out_data: (("row", "chan", "corr"), 
                corrected_data.astype(np.complex64))})
    write = xds_to_table(MS, msname, [options.out_data])

    # Begin writing
    print(f"==> Writing corrected smoother visibilties to `{options.out_data}`")
    with ProgressBar():
        write.compute()

    # Remove ones from gains solutions if DIAG mode
    # TEMP FIX: Should be reconsidered as this is janky
    if mode == "DIAG":
        zeros = np.zeros((n_time, n_ant, n_chan, n_dir, 2))
        filter_gains[..., 1, :] = zeros
        filter_gains[..., 2, :] = zeros
        smooth_gains[..., 1, :] = zeros
        smooth_gains[..., 2, :] = zeros

    # Output filter gains to npy file
    with open(options.out_filter, "wb") as file:
        np.save(file, filter_gains)
    print(f"==> Filter gains saved to `{options.out_filter}`")

    # Output smoother gains to npy file
    with open(options.out_smoother, "wb") as file:
        np.save(file, smooth_gains)    
    print(f"==> Smoother gains saved to `{options.out_smoother}`")

def calibrate_from_arrays(tbin_indices, tbin_counts, 
            ant1, ant2, vis, model, weight, **kwargs):
    """A vanilla calibrate command to use the kalman
    filter and smoother in an ordinary manner from
    explicit data."""

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

    # Get dimensions (correlations need to be adapted)
    n_row, n_chan, n_dir, n_corr = model.shape 

    # Get number of antennas
    n_ant = np.max((np.max(ant1), np.max(ant2))) + 1      

    # Adjust for correlations axis (n_corr to 1)
    model = model[:, :, :, 0]
    vis = vis[:, :, 0]
    weight = weight[:, 0]

    # Create priors
    mp = np.ones((n_ant, n_chan, n_dir, 2), dtype=np.complex128)
    mp = gains_vector(mp)
    Pp = np.eye(mp.size, dtype=np.complex128)

    # Create noise matrices
    if options.sigma_n is None:
        # Temporary fix till weights are adjusted
        options.sigma_n = 1 

    Q = options.sigma_f**2 * np.eye(mp.size, dtype=np.complex128)
    R = 2 * options.sigma_n**2\
        * np.eye(n_ant * (n_ant - 1) * n_chan, dtype=np.complex128) 

    # Variable to keep track of algorithm direction
    a_dir = "forward" 

    # Gains files
    gains_files = []

    # Run Kalman Filter for requested number of times
    total_start = filter_start = time()
    for i in range(options.filter):
        m, P = kalman_filter(mp, Pp, model, vis, weight, Q, R, 
                                ant1, ant2, tbin_indices, 
                                tbin_counts, options.step_control)        

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
                a_dir = "backward"
            elif a_dir == "backward":
                a_dir = "forward"
            
            # Flip arrays
            mp = gains_vector(m[-1])
            Pp = P[-1]
            model = model[::-1]
            vis = vis[::-1]
            weight = weight[::-1]
            tbin_indices = tbin_indices[::-1] # For consistency
            tbin_counts = tbin_counts[::-1] # For consistency
    
    # Output filter gains to npy file
    if (options.which_gains.lower() == "filter"\
        or options.which_gains.lower() == "both")\
        and options.filter > 0:
        gains_files.append("filter_" + options.out_file)
        with open(gains_files[-1], 'wb') as file:            
                np.save(file, m)

    # Stop filter timer and start smoother timer
    filter_time = time() - filter_start
    smoother_start = time()

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
                a_dir = "backward"
            elif a_dir == "backward":
                a_dir = "forward"
            
            # Flip arrays
            m = ms[::-1]
            P = Ps[::-1]

    # Stop time
    stop_time = time()
    total_time = stop_time - total_start
    smoother_time = stop_time - smoother_start

    # Output smoother gains to npy file
    if (options.which_gains.lower() == "smoother"\
        or options.which_gains.lower() == "both")\
        and options.smoother > 0:
        gains_files.append("smoother_" + options.out_file)
        with open(gains_files[-1], 'wb') as file:            
                np.save(file, ms)  

    # Show timer results
    print(f"==> Completed and saved to: {', '.join(gains_files)}")
    print(f"==> {options.filter} filter run(s) "\
          + f"in {np.round(filter_time, 3)} s, "\
          + f"{options.smoother} smoother run(s) "\
          + f"in {np.round(smoother_time, 3)} s, "\
          + f"total taken: {np.round(total_time, 3)} s")