import numpy as np
from kalcal.generation import loader, parser
from kalcal.generation import generate
import packratt


def full(
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
    np.seed(seed)

    # MS name and packratt get name
    msname = f'dataset/ms/KAT7_{n_time}_{n_ant}_{n_chan}.MS'
    pullname = f'/MSC_DATA/MS/KAT7_{n_time}_{n_ant}_{n_chan}.tar.gz'

    # Get ms via packratt
    packratt.get(pullname, dest)

    # Create generate parser
    gen_args = parser.generate_parser().parse_args([])
    lt, lnu, ls = len_scales
    gen_args.ms = msname
    gen_args.sky_model = f'datasets/sky_models/MODEL-{n_dir}.txt'
    gen_args.sigma_n = sigma_n    
    gen_args.lt = lt
    gen_args.lnu = lnu
    gen_args.ls = ls
    gen_args.sigma_f = sigma_f
    
    # Generate jones and apply corruption to data
    generate.both(gen_args)

    # Load the data
    return loader.get_data(gen_args)