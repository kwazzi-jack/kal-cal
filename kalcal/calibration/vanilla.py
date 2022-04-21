from omegaconf import OmegaConf as ocf
from kalcal.filters import ekf
from kalcal.smoothers import eks
from kalcal.tools.utils import gains_vector, concat_dir_axis
from dask import array as da
from daskms import xds_from_ms, xds_to_table
from africanus.calibration.utils import corrupt_vis, correct_vis
import numpy as np
from time import time
import os

# Direction of algorithms
FORWARD = 0
BACKWARD = 1

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

    # Set thread count to cpu count
    if options.ncpu:
        from multiprocessing.pool import ThreadPool
        import dask
        import numba
        dask.config.set(pool=ThreadPool(options.ncpu))
        numba.set_num_threads(n=options.ncpu)
        os.environ["OMP_NUM_THREADS"] = str(int(options.ncpu))
        os.environ["OPENBLAS_NUM_THREADS"] = str(int(options.ncpu))
    else:
        import multiprocessing
        dask.config.set(pool=ThreadPool(multiprocessing.cpu_count()))

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
    if s_model.shape[-1] == 4:
        # All correlations
        corr = [0, 1, 2, 3]

    elif s_model.shape[-1] == 2:
        # First and last correlations
        corr = [0, 1]

    elif s_model.shape[-1] == 1:
        # No correlations
        corr = [0]

    else:
        # (2 x 2) not implemented yet
        raise ValueError("Cannot identify correlation shape.")

    # Gains solutions
    filter_gains = np.zeros((n_time, n_ant, n_chan, n_dir, n_corr, 2),
                                dtype=np.complex128)

    smooth_gains = np.zeros((n_time, n_ant, n_chan, n_dir, n_corr, 2),
                                dtype=np.complex128)

    # Create own weights
    if options.sigma_n is not None:
        cvar = 2 * options.sigma_n**2
        weight = 1.0/cvar * np.ones_like(weight)

    for c in corr:
        # Get data related to correlation
        cmodel = model[..., c]
        cvis = vis[..., c]
        cweight = weight[..., c]

        # Create priors
        mp = np.ones((n_ant, n_chan, n_dir, 2), dtype=np.complex128)
        mp = gains_vector(mp)
        Pp = np.eye(mp.size, dtype=np.complex128)

        # Noise Matrices
        Q = 2 * options.sigma_f * np.eye(mp.size, dtype=np.complex128)
        R = 2 * options.sigma_n\
            * np.eye(n_ant * (n_ant - 1) * n_chan, dtype=np.complex128)

        # Variable to keep track of algorithm direction
        a_dir = FORWARD

        for i in range(options.filter):
            m, P = kalman_filter(mp, Pp, cmodel, cvis, cweight, Q, R,
                                    ant1, ant2, tbin_indices,
                                    tbin_counts, options.step_control)

            # Correct flipping if last iteration
            if i == options.filter - 1:
                if a_dir == BACKWARD:
                    # Reset algorithm direction
                    a_dir = FORWARD

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
                if a_dir == FORWARD:
                    a_dir = BACKWARD
                elif a_dir == BACKWARD:
                    a_dir = FORWARD

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

        # Run Kalman Smoother for requested number of times
        for i in range(options.smoother):
            ms, Ps, _ = kalman_smoother(m, P, Q)

            # Correct flipping if last iteration
            if i == options.smoother - 1:
                if a_dir == BACKWARD:
                    # Reset algorithm direction
                    a_dir = FORWARD

                    # Flip arrays
                    ms = ms[::-1]
                    Ps = Ps[::-1]
            else:
                # Set algorithm direction
                if a_dir == FORWARD:
                    a_dir = BACKWARD
                elif a_dir == BACKWARD:
                    a_dir = FORWARD

                # Flip arrays
                m = ms[::-1]
                P = Ps[::-1]

        # Save smoother gains
        smooth_gains[..., c, :] = ms.copy()

    if options.out_data is not None and options.out_data != "":
        # Set off-diagonals to ones for gains
        jones = np.ones_like(smooth_gains[..., 0])
        jones[..., 0] = smooth_gains[..., 0, 0]
        jones[..., 3] = smooth_gains[..., 0, 0]

        # Correct Visibilties
        corrected_data = correct_vis(
            tbin_indices,
            tbin_counts,
            ant1,
            ant2,
            jones,
            vis,
            flag)

        # To dask
        corrected_data = da.from_array(corrected_data,
                            chunks=MS.get(options.vis_column).chunks)

        # Assign and write to ms
        MS = MS.assign(**{options.out_data: (("row", "chan", "corr"),
                    corrected_data.astype(np.complex64))})

        columns = [options.out_data]

        if options.out_weight is not None and options.out_weight != "":
            abs_sqr_gains = np.power(np.abs(smooth_gains[..., 0]), 2)
            cvar = 2 * options.sigma_n**2
            weight = 1.0/cvar * np.ones((n_row, n_chan, n_dir, n_corr))
            weight_spectrum = corrupt_vis(tbin_indices, tbin_counts, ant1, ant2, abs_sqr_gains, weight).real

            weight_spectrum = da.from_array(weight_spectrum,
                            chunks=MS.get(options.vis_column).chunks)

            MS = MS.assign(**{options.out_weight: (("row", "chan", "corr"),
                    weight_spectrum.astype(np.float32))})

            columns.append(options.out_weight)

        xds_to_table(MS, msname, columns).write()

    # Output filter gains to npy file
    if options.out_filter is not None and options.out_filter != "":
        with open(options.out_filter, "wb") as file:
            np.save(file, filter_gains)

    # Output smoother gains to npy file
    if options.out_smoother is not None and options.out_smoother != "":
        with open(options.out_smoother, "wb") as file:
            np.save(file, smooth_gains)
