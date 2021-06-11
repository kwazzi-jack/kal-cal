from simms import simms
from kalcal.datasets.antenna_tables import (
    KAT7, LOFAR, MEERKAT, SKA197, SKA254,
    VLAA, VLAB, VLAC, VLAD, WSRT
)
from omegaconf import OmegaConf as ocf


# Antenna table paths
antenna_tables = {
    "meerkat"   : MEERKAT,
    "kat-7"     : KAT7,
    "jvla"      : VLAD,
    "vla"       : VLAD,
    "jvla-a"    : VLAA,
    "jvla-b"    : VLAB,
    "jvla-c"    : VLAC,
    "jvla-d"    : VLAD,
    "vla-a"     : VLAA,
    "vla-b"     : VLAB,
    "vla-c"     : VLAC,
    "vla-d"     : VLAD,
    "wsrt"      : WSRT,
    "ska1mid254": SKA254,
    "ska1mid197": SKA197,
    "lofar_nl"  : LOFAR
}


def new(**kwargs):
    """Create a new simple empty measurement set using
    simms, given the arguments parsed."""

    # Options to attributed dictionary
    if kwargs["yaml"] is not None:
        options = ocf.load(kwargs["yaml"])
    else:    
        options = ocf.create(kwargs)    

    # Set to struct
    ocf.set_struct(options, True)
    # Change path to antenna table
    try:
        pos = antenna_tables[options.tel.lower()]        
    except:
        raise ValueError(f"Invalid antenna table selection, "\
            +  "the following are available: "\
            + f"{', '.join(antenna_tables.keys())}")
    
    # Create empty measurment set (design of simms doesn't allow suppressing of output)
    print(f"==> Creating empty ms with `simms`: {options.msname}")  
    simms.create_empty_ms(
        msname=options.msname,
        tel=options.tel,
        pos_type=options.pos_type,
        pos=pos,
        dec=options.dec,
        ra=options.ra,
        synthesis=options.synthesis,
        dtime=options.dtime,
        freq0=options.freq0,
        nchan=options.nchan,
        dfreq=options.dfreq,
        stokes=options.stokes,
        scan_length=[options.synthesis],
        nolog=True)