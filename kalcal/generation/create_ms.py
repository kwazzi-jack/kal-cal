from simms import simms
from kalcal.datasets.antenna_tables import KAT7


def create_ms(args):
    """Create a new empty measurement set using
    simms, given the arguments parsed."""
    
    # Check for antenna table selected
    if args.pos == 'kat-7.itrf.txt':
        args.pos = KAT7
    else:
        raise NotImplemented("Only kat-7 table is supported")

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