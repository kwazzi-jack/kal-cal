import click
from kalcal.create.ms import new as new_cmd


@click.command()
@click.argument("msname", type=str)

@click.option("-t", "--tel", type=str,
                default="kat7", show_default=True,
                help="Name of antenna table to use / "\
                    + "path to antenna table.")

@click.option("-e", "--pos_type", type=str,
                default="ascii", show_default=True,
                help="Encoding used on antenna table.")

@click.option("-d", "--dec", type=str,
                default="-30d0m0s", show_default=True,
                help="Angle of declination.")

@click.option("-r", "--ra", type=str,
                default="0h0m0s", show_default=True,
                help="Angle of right ascension.")

@click.option("-s", "--synthesis", type=int,
                default=5, show_default=True,
                help="Synthesis time (used as default scan-length).")

@click.option("-t", "--dtime", type=int, 
                default=90, show_default=True,
                help="Integration time.")

@click.option("-f", "--freq0", type=str, 
                default="1.4GHz", show_default=True,
                help="Initial frequency in Hertz.")

@click.option("-c", "--nchan", type=str, 
                default="1", show_default=True,
                help="Number of channels to use.")

@click.option("-q", "--dfreq", type=str, 
                default="10MHz", show_default=True,
                help="Integration frequency.")

@click.option("-p", "--stokes", type=str,
                default="XX XY YX YY", show_default=True,
                help="Type of stokes polarization.")

@click.option("-y", "--yaml", type=str,
                help="Path to yaml config file.")

def ms(msname, **kwargs):
    """Create command to make a new empty measurement set using
    `simms` with some added features to make it easier to create."""

    return new_cmd(msname, **kwargs)