import click
from kalcal.create.gains import new as new_cmd


@click.command()
@click.argument("ms", type=str)
@click.argument("sky_model", type=str)

@click.option("-t", "--type", 
                type=click.Choice(["phase", "normal"], case_sensitive=False),
                default="normal", show_default=True,
                help="Choose between phase-only or normal gains to generate.")

@click.option("-s", "--std", type=float, 
                default=1.0, show_default=True,
                help="Standard deviation in (normal) time-axis or (phase) "\
                     + "alphas for a phase-screen basis function.")

@click.option("-d", "--diffs", type=float, 
                default=[0.05, 0.05, 0.5], show_default=True, nargs=3,
                help="If (normal), chooses differentials in [time, freq, dir] "\
                     + "else (phase) it does nothing.")

@click.option("-e", "--die", is_flag=True, 
                help="Flag to set if gains are direction independent.")

@click.option("-o", "--out_file", type=str,
                default="gains.npy", show_default=True,
                help="Name of gains output .npy file with gains type appended.")

@click.option("-y", "--yaml", type=str,
                help="Path to yaml config file.")

def gains(ms, sky_model, **kwargs):
    """Create command to simulate either normal or phase-only
    gains for a given measurement set and sky-model."""

    return new_cmd(ms, sky_model, **kwargs)