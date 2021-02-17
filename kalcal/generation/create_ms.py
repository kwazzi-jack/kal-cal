from simms import simms
from .parser import create_ms_parser


def create_ms(args):
    """Create a new empty measurement set using
    simms, given the arguments parsed."""
    
    # Create empty measurment set    
    simms.create_empty_ms(
        msname=args.msname,
        tel=args.tel,
        pos_type=args.pos_type,
        pos=args.pos,
        dec=args.dec,
        ra=args.ra,
        synthesis=args.synthesis,
        dtime=args.dtime,
        freq0=args.freq0,
        nchan=args.nchan,
        dfreq=args.dfreq,
        stokes=args.stokes,
        nolog=True)

if __name__ == "__main__":
    pass