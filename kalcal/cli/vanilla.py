import click
from kalcal.calibration.vanilla import calibrate as calibrate_cmd


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
                help="Path to yaml config file.")

def vanilla(ms, **kwargs):
    """Vanilla calibrate command with the assumption of a single
    correlation and no directions to calibrate for. Designed 
    as a simple implementation of the Kalman and Filter algorithm
    to get to grips with how it works."""

    return calibrate_cmd(ms, **kwargs)