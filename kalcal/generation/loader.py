import numpy as np
from africanus.calibration.utils import chunkify_rows
import dask.array as da
from daskms import xds_from_table
from kalcal.tools.utils import concat_dir_axis

def get_data(args, fmt='numpy'):
    """ Load gains and ms data from generate.py
    args."""

    # MS name
    ms_file = args.ms

    # Load ms
    ms = xds_from_table(ms_file)[0]   

    # Get time-bin indices and counts, normalising the scale to start from 0
    _, tbin_indices, tbin_counts = chunkify_rows(ms.TIME, 1)
    tbin_indices -= tbin_indices.min()
    
    # Get antenna tables
    ant1 = ms.ANTENNA1.data
    ant2 = ms.ANTENNA2.data
    
    # Get corrupted data
    vis = ms.DATA.data[:, :, 0]

    # Concatenate source models in direction column and remove
    # correlation axis
    model = concat_dir_axis(ms)[:, :, :, 0]

    # Get weight column, removing correlation axis
    weight = ms.WEIGHT.data[:, 0]

    # Gains name
    if args.out == '':
        args.out = f"{args.mode}.npy"  
    
    # Load gains data
    jones = None
    with open(args.out, 'rb') as file:
        jones = np.load(file)

    # Remove correlation axis on jones term
    jones = jones[:, :, :, :, 0].astype(np.complex128)  

    # Format to numpy arrays
    if fmt == "numpy":
        ant1 = ant1.compute()
        ant2 = ant2.compute()
        vis = vis.compute().astype(np.complex128)
        model = model.compute().astype(np.complex128)
        weight = weight.compute().astype(np.complex128)
    # Format to dask arrays
    elif fmt == "dask":
        # Jones dimensions
        n_ant, _, n_chan, n_dir = jones.shape

        # Chunking scheme
        jones_chunks = (n_ant, 1, n_chan, n_dir)

        # Jones to dask
        jones = da.from_array(jones, chunks=jones_chunks)

    return tbin_indices, tbin_counts, ant1, ant2,\
            vis, model, weight, jones