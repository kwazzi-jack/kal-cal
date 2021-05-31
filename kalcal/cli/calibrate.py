import click
from omegaconf import OmegaConf as ocf
from kalcal.filters import ekf

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
                type=click.Choice(["NUMBA", "SPARSE"]),
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

@click.option("-o", "--out_file", type=str,
                default="gains.npy", show_default=True,
                help="Name of calibrated gains output .npy file.")

@click.option("-y", "--yaml", type=str,
                default="",
                help="Path to yaml config file.")

def calibrate(ms, **kwargs):

    # Options to attributed dictionary
    options = ocf.create(kwargs)

    # If config file exists, overwrite options
    if options.yaml != "":
        options = ocf.load(options.yaml)

    # Check extensions on ms
    if ms.split(".")[-1].lower() != "ms":
        raise ValueError(f"'{ms}' does not have a valid MS extension.")

    # Choose algorithm
    if options.algorithm.upper() == "NUMBA":
        kalman_filter = ekf.numpy     