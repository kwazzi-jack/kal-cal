import numpy as np
import Tigger
import dask.array as da 
from daskms import xds_from_ms, xds_from_table, xds_to_table
from africanus.coordinates import radec_to_lm
from africanus.calibration.utils import chunkify_rows
from africanus.dft.dask import im_to_vis
from africanus.model.coherency.dask import convert
from africanus.calibration.utils.dask import corrupt_vis
from kalcal.datasets.sky_models import (
    MODEL_1, MODEL_4, MODEL_50
)
from omegaconf import OmegaConf as ocf


# Sky-model paths
sky_models = {
    "model-1"    : MODEL_1,
    "model-4"    : MODEL_4,
    "model-50"   : MODEL_50
}


def new(ms, sky_model, gains, **kwargs):
    """Generate model visibilties per source (as direction axis)
    for stokes I and Q and generate relevant visibilities."""

    # Options to attributed dictionary
    if kwargs["yaml"] is not None:
        options = ocf.load(kwargs["yaml"])
    else:    
        options = ocf.create(kwargs)    

    # Set to struct
    ocf.set_struct(options, True)

    # Change path to sky model if chosen
    try:
        sky_model = sky_models[sky_model.lower()]        
    except:
        # Own sky model reference
        pass
    
    # Set thread count to cpu count
    if options.ncpu:
        from multiprocessing.pool import ThreadPool
        import dask
        dask.config.set(pool=ThreadPool(options.ncpu))
    else:
        import multiprocessing
        options.ncpu = multiprocessing.cpu_count()

    # Load gains to corrupt with
    with open(gains, "rb") as file:
        jones = np.load(file)
    
    # Load dimensions
    n_time, n_ant, n_chan, n_dir, n_corr = jones.shape
    n_row = n_time * (n_ant * (n_ant - 1)//2)

    # Load ms
    MS = xds_from_ms(ms)[0]

    # Get time-bin indices and counts
    row_chunks, tbin_indices, tbin_counts = chunkify_rows(
        MS.TIME, options.utime)

    # Close and reopen with chunked rows
    MS.close()
    MS = xds_from_ms(ms, chunks={"row": row_chunks})[0]

    # Get antenna arrays (dask ignored for now)
    ant1 = MS.ANTENNA1.data
    ant2 = MS.ANTENNA2.data    

    # Adjust UVW based on phase-convention
    if options.phase_convention.upper() == 'CASA':
        uvw = -MS.UVW.data.astype(np.float64)
    elif options.phase_convention.upper() == 'CODEX':
        uvw = MS.UVW.data.astype(np.float64)
    else:
        raise ValueError("Unknown sign convention for phase.")
    
    # MS dimensions
    dims = ocf.create(dict(MS.sizes))

    # Close MS
    MS.close()

    # Build source model from lsm
    lsm = Tigger.load(sky_model)

    # Check if dimensions match jones    
    assert n_time * (n_ant * (n_ant - 1)//2) == dims.row
    assert n_time == len(tbin_indices)
    assert n_ant == np.max((np.max(ant1), np.max(ant2))) + 1
    assert n_chan == dims.chan
    assert n_corr == dims.corr       

    # If gains are DIE    
    if options.die: 
        assert n_dir == 1
        n_dir = len(lsm.sources)
    else:
        assert n_dir == len(lsm.sources)

    # Get phase direction
    radec0_table = xds_from_table(ms + '::FIELD')[0]
    radec0 = radec0_table.PHASE_DIR.data.squeeze().compute()
    radec0_table.close()

    # Get frequency column
    freq_table = xds_from_table(ms + '::SPECTRAL_WINDOW')[0]
    freq = freq_table.CHAN_FREQ.data.astype(np.float64)[0]
    freq_table.close()

    # Get feed orientation
    feed_table = xds_from_table(ms + '::FEED')[0]
    feeds = feed_table.POLARIZATION_TYPE.data[0].compute()

    # Create initial model array
    model = np.zeros((n_dir, n_chan, n_corr), dtype=np.float64)

    # Create initial coordinate array and source names
    lm = np.zeros((n_dir, 2), dtype=np.float64)
    source_names = []

    # Cycle coordinates creating a source with flux
    for d, source in enumerate(lsm.sources):
        # Extract name
        source_names.append(source.name)

        # Extract position
        radec_s = np.array([[source.pos.ra, source.pos.dec]])
        lm[d] =  radec_to_lm(radec_s, radec0)

        # Get flux - Stokes I
        if source.flux.I:
            I0 = source.flux.I

            # Get spectrum (only spi currently supported)
            tmp_spec = source.spectrum
            spi = [tmp_spec.spi if tmp_spec is not None else 0.0]
            ref_freq = [tmp_spec.freq0 if tmp_spec is not None else 1.0]

            # Generate model flux
            model[d, :, 0] = I0 * (freq/ref_freq)**spi

        # Get flux - Stokes Q
        if source.flux.Q:
            Q0 = source.flux.Q

            # Get spectrum
            tmp_spec = source.spectrum
            spi = [tmp_spec.spi if tmp_spec is not None else 0.0]
            ref_freq = [tmp_spec.freq0 if tmp_spec is not None else 1.0]

            # Generate model flux
            model[d, :, 1] = Q0 * (freq/ref_freq)**spi

        # Get flux - Stokes U
        if source.flux.U:
            U0 = source.flux.U

            # Get spectrum
            tmp_spec = source.spectrum
            spi = [tmp_spec.spi if tmp_spec is not None else 0.0]
            ref_freq = [tmp_spec.freq0 if tmp_spec is not None else 1.0]

            # Generate model flux
            model[d, :, 2] = U0 * (freq/ref_freq)**spi

        # Get flux - Stokes V
        if source.flux.V:
            V0 = source.flux.V

            # Get spectrum
            tmp_spec = source.spectrum
            spi = [tmp_spec.spi if tmp_spec is not None else 0.0]
            ref_freq = [tmp_spec.freq0 if tmp_spec is not None else 1.0]

            # Generate model flux
            model[d, :, 3] = V0 * (freq/ref_freq)**spi

    # Close sky-model
    del lsm
    
    # Build dask graph
    tbin_indices = da.from_array(tbin_indices, chunks=(options.utime))
    tbin_counts = da.from_array(tbin_counts, chunks=(options.utime))
    lm = da.from_array(lm, chunks=lm.shape)
    model = da.from_array(model, chunks=model.shape)
    jones = da.from_array(jones, chunks=(options.utime,) + jones.shape[1::])
    
    # Apply image to visibility for each source
    sources = []
    for s in range(n_dir):
        source_vis = im_to_vis(model[s].reshape((1, n_chan, n_corr)), uvw, 
                        lm[s].reshape((1, 2)), freq, dtype=np.complex64, 
                        convention='fourier')

        sources.append(source_vis)
    model_vis = da.stack(sources, axis=2)

    # Sum over direction?
    if options.die:
        model_vis = da.sum(model_vis, axis=2, keepdims=True)
        n_dir = 1
        source_names = [options.mname] 

    # Select schema based on feed orientation
    if (feeds == ["X", "Y"]).all():
        out_schema = [["XX", "XY"], ["YX", "YY"]]
    elif (feeds == ["R", "L"]).all():
        out_schema = [['RR', 'RL'], ['LR', 'LL']]
    else:
        raise ValueError("Unknown feed orientation implementation.")

    # Convert Stokes to Correlations
    in_schema = ['I', 'Q', 'U', 'V']
    model_vis = convert(model_vis, in_schema, out_schema).reshape(
                    (n_row, n_chan, n_dir, n_corr))
    
    # Apply gains to model_vis
    data = corrupt_vis(tbin_indices, tbin_counts, ant1, ant2,
                            jones, model_vis)

    # Reopen MS
    MS = xds_from_ms(ms, chunks={"row": row_chunks})[0]
    
    # Assign model visibilities
    out_names = []
    for d in range(n_dir):
        MS = MS.assign(**{source_names[d]: 
                (("row", "chan", "corr"), 
                model_vis[:, :, d].astype(np.complex64))})

        out_names += [source_names[d]]

    # Assign noise free visibilities to 'CLEAN_DATA'
    MS = MS.assign(**{'CLEAN_' + options.dname: (("row", "chan", "corr"), 
            data.astype(np.complex64))})

    out_names += ['CLEAN_' + options.dname]
    
    # Get noise realisation
    if options.std > 0.0:
    
        # Noise matrix
        noise = []
        for i in range(2):
            real = da.random.normal(loc=0.0, scale=options.std, 
                        size=(n_row, n_chan), 
                        chunks=(row_chunks, n_chan))
            imag = 1.0j*(da.random.normal(loc=0.0, scale=options.std, 
                        size=(n_row, n_chan), 
                        chunks=(row_chunks, n_chan)))
            noise.append(real + imag)


        # Zero matrix for off-diagonals
        zero = da.zeros((n_row, n_chan), chunks=(row_chunks, n_chan))

        noise.insert(1, zero)
        noise.insert(2, zero)

        # NP to Dask
        noise = da.stack(noise, axis=2).rechunk((
                    row_chunks, n_chan, n_corr))

        # Assign noise to 'NOISE'
        MS = MS.assign(**{'NOISE': (("row", "chan", "corr"), 
                noise.astype(np.complex64))})

        out_names += ['NOISE']

        # Add noise to data and assign to 'DATA'
        noisy_data = data + noise
        
        MS = MS.assign(**{options.dname: (("row", "chan", "corr"), 
                noisy_data.astype(np.complex64))})

        out_names += [options.dname]
    
    # Create a write to the table
    xds_to_table(MS, ms, out_names).compute()