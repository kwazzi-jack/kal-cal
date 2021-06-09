from simms import simms
from kalcal.datasets.antenna_tables import (
    KAT7, LOFAR, MEERKAT, SKA197, SKA254,
    VLAA, VLAB, VLAC, VLAD, WSRT
)


# Antenna table paths
antenna_tables = {
    "kat7"   : KAT7,
    "lofar"   : LOFAR,
    "meerkat" : MEERKAT,
    "ska197"  : SKA197,
    "ska254"  : SKA254,
    "vlaa"    : VLAA,
    "vlab"    : VLAB,
    "vlac"    : VLAC,
    "vlad"    : VLAD,
    "wrst"    : WSRT
}


def create_empty_ms(args):
    """Create a new simple empty measurement set using
    simms, given the arguments parsed."""
    
    # Change path to antenna table
    try:
        args.pos = antenna_tables[args.pos.lower()]
    except:
        raise ValueError(f"Invalid antenna-table selection,")

    # Create empty measurment set  
    print(f"==> Creating empty ms: {args.msname}")  
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
        scan_length=[args.synthesis],
        nolog=True)