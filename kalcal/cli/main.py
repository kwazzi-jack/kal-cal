import click
from kalcal.cli.vanilla import vanilla
from kalcal.cli.ms import ms


# Commands for kal-calibrate 
@click.group()
def kalcal_calibrate():
    pass


# Commands for kal-create
@click.group()
def kalcal_create():
    pass


# Add commands to kal-calibrate
kalcal_calibrate.add_command(vanilla)


# Add commands to kal-create
kalcal_create.add_command(ms)