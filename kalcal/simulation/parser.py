import argparse
import yaml


def create_ms_parser():
    """Parser object for settings of create_ms.py."""
    p = argparse.ArgumentParser()

    # Measurement Set Name
    p.add_argument("--msname", help="Name of MS.", type=str,
                    default="KALMAN_SET.MS")

    # Antenna table name
    p.add_argument("--tel", help="Antenna table to use.", 
                    type=str, default='kat-7')

    # Table encoding type
    p.add_argument("--pos_type", help="Table encoding type.",
                    type=str, default="ascii")

    # Antenna table position
    p.add_argument("--pos", help="Antenna table position.", 
                    type=str, default='kat-7.itrf.txt')

    # Declination of MS
    p.add_argument("--dec", help="Declination position of MS.", 
                    type=str, default="-30d0m0s")

    # Right Ascension of MS
    p.add_argument("--ra", help="Right Ascension position of MS.", 
                    type=str, default="0h0m0s")    

    # Scan length
    p.add_argument("--synthesis", help="Synthesis time in hours.",
                    default=5, type=int)

    # Integration Time
    p.add_argument("--dtime", type=int, default=90, 
                    help="Integration time in seconds.")
    
    # Initial Frequency
    p.add_argument("--freq0", type=str, default="1.4GHz", 
                    help="Starting frequency of MS.")

    # Number of Channels
    p.add_argument("--nchan", help="Number of frequency channels.", 
                    type=str, default="1")

    # Frequency Interval
    p.add_argument("--dfreq", help="Frequency interval between channels.", 
                    type=str, default="10MHz")

    # Polarisation mode
    p.add_argument("--stokes", help="Polarisation mode of MS.", 
                    type=str, default="RR RL LR LL")

    # Return parser
    return p


def from_ms_parser():
    """Parser object for settings of from_ms.py."""
    p = argparse.ArgumentParser()
    
    # Measurement Set
    p.add_argument("--ms", help="Name of measurement set.", type=str)

    # Generation mode of Gains
    p.add_argument("--mode", help="Phase-only or Normal Gains.",
                    type=str, default="normal")

    # Sky Model (LSM file)
    p.add_argument("--sky_model", type=str, help="Tigger LSM file.")

    # Chunking scheme for time-axis
    p.add_argument("--utimes_per_chunk",  default=1, type=int,
                    help="Number of unique times in each chunk.")

    # Number of CPU cores
    p.add_argument("--ncpu", help="The number of threads to use. "\
                    + "Default of zero means all.", default=10, type=int)

    # Alpha Values Std Deviation for Phase Mode
    p.add_argument("--alpha_std", type=float, default=0.1, 
                    help="Standard deviation of alpha-"\
                    + "values of phase screen.")
    
    # Noise on Visibilities Std Deviation
    p.add_argument("--sigma_n", type=float, default=0.1, 
                    help="Standard deviation of the noise on "\
                        "the visibilities.")

    # Time length Scale
    p.add_argument("--lt", help="Length scale of time-axis.", 
                    type=float, default=0.05)

    # Frequency length Scale
    p.add_argument("--lnu", help="Length scale of frequency-axis.", 
                    type=float, default=0.05)

    # Direction length Scale
    p.add_argument("--ls", help="Length scale of direction-axis.", 
                    type=float, default=0.5)

    # Variance of gains in Normal Mode
    p.add_argument("--sigma_f", help="Standard deviation on generated "\
                    + "normal-gains.", type=float, default=1.0)

    # Phase Convention
    p.add_argument("--phase_convention", type=str, default='CODEX', 
                    help="The convention to use for the sigma of the "\
                    + "phase delay. Options are 'CASA' -> positive "\
                    + "phase or 'CODEX' -> negative phase.")

    # Output Filename
    p.add_argument("--out", help="Name of gains output npy file. "\
                    + "Empty name indicates filename generation.", 
                    type=str, default="")

    # Return parser
    return p


def yaml_parser(filename):
    """Create a parser object, but with settings from a
    yaml file."""

    try:
        with open(filename, 'r') as file:
            # Read yaml file
            config = yaml.load(file, Loader=yaml.FullLoader)

            # Create create ms parser and fill with settings from
            # config file
            cms_par = create_ms_parser()
            cmdline = []
            for key, val in config['create_ms'].items():
                cmdline.append(f"--{key}")
                cmdline.append(str(val))

            # Create new args 
            cms_args = cms_par.parse_args(cmdline)

            # Create from ms parser and fill with settings from
            # config file
            fms_par = from_ms_parser()
            cmdline = []
            for key, val in config['from_ms'].items():
                cmdline.append(f"--{key}")
                cmdline.append(str(val))

            # Create new args 
            fms_args = fms_par.parse_args(cmdline)            

            return {'create_ms' : cms_args, 
                        'from_ms' : fms_args}
    except:
        raise IOError('Config-file does not exist.')