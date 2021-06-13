import click
from kalcal.cli import calibrate_vanilla
from kalcal.cli import create_ms
from kalcal.cli import create_gains
from kalcal.cli import create_data
from kalcal.cli import plot_gains


# Commands for kal-calibrate 
@click.group()
def kalcal_calibrate():
    pass


# Commands for kal-create
@click.group()
def kalcal_create():
    pass


# Commands for kal-plot
@click.group()
def kalcal_plot():
    pass


# Add commands to kal-calibrate
kalcal_calibrate.add_command(calibrate_vanilla.vanilla)

# Add commands to kal-create
kalcal_create.add_command(create_ms.ms)
kalcal_create.add_command(create_gains.gains)
kalcal_create.add_command(create_data.data)

# Add commands to kal-plot
kalcal_plot.add_command(plot_gains.gains)