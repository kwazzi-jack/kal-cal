import click
from kalcal.create.data import new as new_cmd


@click.command()
@click.argument("ms", type=str)
@click.argument("sky_model", type=str)
@click.argument("gains", type=str)

@click.option("-s", "--std", type=float, 
                default=0.1, show_default=True,
                help="Standard deviation for zero-mean noise applied to visibilities.")

@click.option("-c", "--phase_convention", 
                type=click.Choice(["CASA", "CODEX"], case_sensitive=False),
                default="CODEX", show_default=True,
                help="Choose phase-convention for UVW coordinates.")

@click.option("-e", "--die", is_flag=True, 
                help="Flag to set if gains are direction independent.")

@click.option("-u", "--utime", type=int, 
                default=1, show_default=True,
                help="Number of unique times per chunk for dask chunking.")

@click.option("-n", "--ncpu", type=int, 
                default=-1, show_default=True,
                help="Number of cpu-cores for dask to use. For all, use -1.")

@click.option("-y", "--yaml", type=str,
                help="Path to yaml config file.")

def data(ms, sky_model, gains, **kwargs):
    """Generate model visibilties per source (as direction axis)
    for stokes I and Q and generate relevant visibilities."""

    return new_cmd(ms, sky_model, gains, **kwargs)