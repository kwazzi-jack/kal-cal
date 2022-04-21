import click
import oyaml as yl
from omegaconf import OmegaConf as ocf
import subprocess, os, tempfile
from kalcal.cli import calibrate_vanilla
from kalcal.cli import calibrate_cheater
from kalcal.cli import create_ms
from kalcal.cli import create_gains
from kalcal.cli import create_data
from kalcal.cli import plot_gains


# Main command for kalcal
@click.command()
@click.argument("yaml", type=str)
def kalcal_main(yaml):
    """Main kalcal command to call sub-commands from a yaml config
    file. Ordering is important as it indicates order of execution
    of each command."""
    
    # Options to dictionary
    with open(yaml, 'r') as file:        
        options = yl.load(file, Loader=yl.FullLoader) 

    # Go through each step and run command
    # with appropriate settings
    for _, exec_block in options.items():       

        # Get command and subcommand
        topcmd, subcmd = exec_block["command"].split()

        # Get arguments for function
        try:
            args = list(exec_block["arguments"].values())
        except:
            args = []

        # Get options for function
        try:
            kwargs = yl.dump(exec_block["options"])    
        except:
            kwargs = None

        # Create temp config yaml file
        filename, path = tempfile.mkstemp()

        # Dump kwargs into config file
        try:
            with os.fdopen(filename, 'w') as tmp:
                yl.dump(kwargs, tmp)
        except:
            pass

        # Build command
        cmd = [topcmd, subcmd, "--yaml", path] + args
        
        # Run and wait
        proc = subprocess.Popen(cmd)
        proc.wait()

        # Remove config file
        os.remove(path)        

        # Stop if command failed
        if proc.returncode > 0:
            exit()


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
kalcal_calibrate.add_command(calibrate_cheater.cheater)

# Add commands to kal-create
kalcal_create.add_command(create_ms.ms)
kalcal_create.add_command(create_gains.gains)
kalcal_create.add_command(create_data.data)

# Add commands to kal-plot
kalcal_plot.add_command(plot_gains.gains)
