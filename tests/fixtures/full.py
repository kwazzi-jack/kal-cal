import numpy as np
from kalcal.generation import loader, parser
from kalcal.generation import from_params
from os import path
import tarfile
from pkg_resources import resource_filename


def data(
    n_time, 
    n_ant, 
    n_chan, 
    n_dir,
    sigma_n,
    sigma_f,
    seed,
    len_scales,
    dest
):
    """Create mock data in full from measurement set
    and gains file to simulate physical data."""

    # Set the seed
    np.random.seed(seed)

    # MS name and tar-file name
    msname = path.join(dest, f'KAT7_{n_time}_{n_ant}_{n_chan}.MS')
    tarname = f'KAT7_{n_time}_{n_ant}_{n_chan}.tar.gz'

    tarpath = resource_filename('kalcal', 
            path.join('datasets/ms/', tarname))

    # Untar the file
    with tarfile.open(tarpath, 'r:gz') as file:
        file.extractall(dest) 

    # Create generate parser
    gen_args = parser.from_ms_parser().parse_args([])
    lt, lnu, ls = len_scales
    gen_args.ms = msname
    gen_args.sky_model = f'MODEL-{n_dir}.txt'
    gen_args.sigma_n = sigma_n    
    gen_args.lt = lt
    gen_args.lnu = lnu
    gen_args.ls = ls
    gen_args.sigma_f = sigma_f
    
    # Generate jones and apply corruption to data
    from_params.both(gen_args)
       

    # Load the data
    return loader.get_data(gen_args)