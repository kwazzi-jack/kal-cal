import click
from kalcal.cli.calibrate import calibrate


@click.group(invoke_without_command=True)
def group():
    pass

group.add_command(calibrate)