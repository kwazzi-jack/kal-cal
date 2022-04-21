import click
from kalcal.calibration.cheater import calibrate as calibrate_cmd


@click.command()
@click.argument("ms", type=str)

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

@click.option("-q", "--sigma-f", type=float, 
                default=0.1, show_default=True,
                help="State noise for the gains evolution system.")

@click.option("-r", "--sigma-n", type=float,
                help="Measurement noise for the visibilities evolution system, "\
                    + "otherwise inferred via weights from ms.")

@click.option("--step-control", type=float, 
                default=1/2, show_default=True,
                help="Step-control on filter update step.")

@click.option("--true-gains", type=str, 
                help="Path to true-gains used to create corrupted visbilities."\
                    + "It is used to set the first prior state estimate,"\
                    + "to imitate maximum-likelihood estimate start.")

@click.option("--model-column", type=str, 
                default="MODEL_VIS", show_default=True,
                help="Name of ms column with model visibilities. If there "\
                    + "are multiple columns, comma separate them and add "\
                    + "quotations to indicate a string.")

@click.option("--vis-column", type=str, 
                default="DATA", show_default=True,
                help="Name of ms column with data visibilities.")

@click.option("--weight-column", type=str, 
                default="WEIGHT", show_default=True,
                help="Name of ms column with weights.")

@click.option("--out-filter", type=str, 
                default="filter.npy", show_default=True,
                help="Output .npy file for filter calibrated gains.")

@click.option("--out-smoother", type=str, 
                default="smoother.npy", show_default=True,
                help="Output .npy file for smoother calibrated gains.")

@click.option("--out-data", type=str, 
                default="CORRECTED_DATA", show_default=True,
                help="Name of ms column to put corrected data in.")

@click.option("--out-weight", type=str, 
                default="WEIGHT_SPECTRUM", show_default=True,
                help="Name of ms column to put scaled imaging weights in.")

@click.option("--ncpu", type=int,
                help="Number of CPUs allowed for numba and dask to use. Default is all.")

@click.option("-y", "--yaml", type=str,
                help="Path to yaml config file.")

def cheater(ms, **kwargs):
    """Cheater calibrate command works in the same way vanilla
    with the difference that we are given a maximum-likelihood
    prior start (m_0 known and P_0 = Q), allowing us to 'cheat'
    the time taken to start tracking."""

    return calibrate_cmd(ms, **kwargs)
