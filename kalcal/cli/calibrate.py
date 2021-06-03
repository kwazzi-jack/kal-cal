from kalcal.generation import from_ms
import click
from omegaconf import OmegaConf as ocf
from kalcal.filters import ekf
from kalcal.smoothers import eks
from kalcal.tools.utils import gains_vector
from daskms import xds_from_ms
import numpy as np


@click.group()
def group():
    pass


@group.command()
@click.argument("ms")
@click.option("-f", "--filter", type=int,
                default=1, show_default=True,
                help="Number of Kalman Filter runs.")

@click.option("-s", "--smoother", type=int,
                default=1, show_default=True,
                help="Number of RTS Smoother runs.")

@click.option("-a", "--algorithm", 
                type=click.Choice(["NUMBA", "SPARSE"], case_sensitive=False),
                default="NUMBA", show_default=True,
                help="Algorithm optimization to use for the filter.")

@click.option("-q", "--sigma_f", type=float, 
                default=0.1, show_default=True,
                help="State noise for the gains evolution system.")

@click.option("-r", "--sigma_n", type=float,
                help="Measurement noise for the visibilities evolution system, "\
                    + "otherwise inferred via weights from ms.")

@click.option("-c", "--step_control", type=float, 
                default=1/2, show_default=True,
                help="Step-control on filter update step.")

@click.option("-m", "--model_column", type=str, 
                default="MODEL_VIS", show_default=True,
                help="Name of ms column with model visibilities.")

@click.option("-v", "--vis_column", type=str, 
                default="DATA", show_default=True,
                help="Name of ms column with data visibilities.")

@click.option("-w", "--weight_column", type=str, 
                default="WEIGHT", show_default=True,
                help="Name of ms column with weights.")

@click.option("-o", "--out_file", type=str,
                default="gains.npy", show_default=True,
                help="Name of calibrated gains output .npy file.")

@click.option("-w", "--which_gains",
                type=click.Choice(["SMOOTHER", "FILTER", "BOTH"], case_sensitive=False),
                default="SMOOTHER", show_default=True,
                help="Which calibrated gains should be outputted?")

@click.option("-y", "--yaml", type=str,
                default="",
                help="Path to yaml config file.")

def calibrate(ms, **kwargs):

    # Options to attributed dictionary
    options = ocf.create(kwargs)

    # If config file exists, overwrite options
    if options.yaml != "":
        options = ocf.load(options.yaml)

    # Set to struct
    ocf.set_struct(options, True)

    # Check extensions on ms
    if "ms" not in ms.split(".")[-1].lower():
        raise ValueError(f"'{ms}' does not have a valid MS extension.")

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
    n_dir = 1
    n_corr = 1

    # Load model visibilities (dask ignored for now)
    model = MS.get(options.model_column).data.reshape(
        dims.row, dims.chan, 1, dims.corr).compute().astype(np.complex128)

    # Load data visibilities (dask ignored for now)
    vis = MS.get(options.vis_column).data.compute().astype(np.complex128)

    # Load weights (dask ignored for now)
    weight = MS.get(options.weight_column).data.compute().astype(np.complex128)

    # Get time-bin indices and counts
    _, tbin_indices, tbin_counts = np.unique(MS.TIME,
                                        return_index=True, 
                                        return_counts=True)   

    # Set time dimension
    n_time = len(tbin_indices)

    # Get antenna arrays (dask ignored for now)
    ant1 = MS.ANTENNA1.data.compute()
    ant2 = MS.ANTENNA2.data.compute()

    # Set antenna dimension
    n_ant = np.max((np.max(ant1), np.max(ant2))) + 1

    # Adjust for correlations axis
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

    import matplotlib.pyplot as plt

    with open("gains.npy", "rb") as file:
        jones = np.load(file)

    x = np.arange(n_time)
    gpq = jones[:, 0, 0, 0, 0] * jones[:, 1, 0, 0, 0].conj()
    mpq = m[:, 0, 0, 0, 0] * m[:, 1, 0, 0, 0].conj() 
    spq = ms[:, 0, 0, 0, 0] * ms[:, 1, 0, 0, 0].conj()
    plt.plot(x, gpq.real, 'k-')
    plt.plot(x, mpq.real, 'r.')
    plt.plot(x, spq.real, 'g-')
    plt.show()
    exit()
    # Output to wanted gains to npy file
    if options.which_gains.lower() == "smoother":
        with open("smoother_" + options.out_file, 'wb') as file:            
                np.save(file, ms)
    elif options.which_gains.lower() == "filter":
        with open("filter_" + options.out_file, 'wb') as file:            
                np.save(file, m)
    elif options.which_gains.lower() == "both":
        with open(options.out_file, 'wb') as file:            
                np.save(file, m)
                np.save(file, ms)