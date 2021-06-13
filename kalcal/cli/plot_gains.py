import click
from kalcal.plotting.plot import gains as gains_cmd


@click.command()
@click.option("-p", "--plot", 
                type=click.Tuple([str, str, str, str]),
                multiple=True, nargs=4,
                help="Main plot option that requires: "\
                    + "(1) .npy file for gains, "\
                    + "(2) label for gains, "\
                    + "(3) color for gains, "\
                    + "(4) linestyle for gains.")

@click.option("-r", "--ref_ant", type=int,
                default=0, show_default=True,
                help="Reference antenna to plot against.")

@click.option("-s", "--show", type=str,
                default="-1", show_default=True,
                help="Decide which antennas to plot. Must be a "\
                    + "comma separated string. To show all, use -1.")

@click.option("-a", "--axis",
                type=click.Choice(["TIME", "FREQ"], case_sensitive=False),
                default="TIME", show_default=True,
                help="Which jones-axis to plot as x-axis.")

@click.option("-c", "--complex_axis",
                type=click.Choice(["REAL", "IMAG"], case_sensitive=False),
                default="REAL", show_default=True,
                help="Which jones-axis to plot as x-axis.")

@click.option("-t", "--title", type=str,
                help="Optional title for plot.")

@click.option("-o", "--out_file", type=str,
                default="gains_plot.png", show_default=True,
                help="Name of file to save plot too.")

@click.option("-d", "--display", is_flag=True, 
                help="Flag to show plot at end via matplotlib.")

@click.option("-y", "--yaml", type=str,
                help="Path to yaml config file.")

def gains(**kwargs):
    """Plot gains-magnitude value for each antenna q in, 
    g_p x g_q^*, where p is the reference antenna for each 
    jones data present in args."""

    return gains_cmd(**kwargs)