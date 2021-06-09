import Tigger
import dask.array as da
from dask.diagnostics import ProgressBar
from daskms import xds_from_ms, xds_to_table, xds_from_table
from africanus.dft.dask import im_to_vis
from africanus.coordinates import radec_to_lm
from africanus.calibration.utils import chunkify_rows
from africanus.calibration.utils.dask import corrupt_vis
from africanus.model.coherency.dask import convert

from kalcal.generation.normal_gains import normal_gains
from kalcal.generation.phase_gains import phase_gains
from kalcal.datasets.sky_models import (MODEL_1, 
    MODEL_4, MODEL_50)

import numpy as np


def jones(args):
    """Generate jones matrix only, but based off
    of a measurement set."""
    
    # Set thread count to cpu count
    if args.ncpu:
        from multiprocessing.pool import ThreadPool
        import dask
        dask.config.set(pool=ThreadPool(args.ncpu))
    else:
        import multiprocessing
        args.ncpu = multiprocessing.cpu_count()

    # Get full time column and compute row chunks
    ms = xds_from_table(args.ms)[0]
   
    _, tbin_idx, tbin_counts = chunkify_rows(
        ms.TIME, args.utimes_per_chunk)
    
    # Convert time rows to dask arrays
    tbin_idx = da.from_array(tbin_idx, 
                 chunks=(args.utimes_per_chunk))
    tbin_counts = da.from_array(tbin_counts, 
                    chunks=(args.utimes_per_chunk))

    # Time axis
    n_time = tbin_idx.size

    # Get antenna columns
    ant1 = ms.ANTENNA1.data
    ant2 = ms.ANTENNA2.data

    # No. of antennas axis
    n_ant = (np.maximum(ant1.max(), ant2.max()) + 1).compute()

    # Get flag column
    flag = ms.FLAG.data

    # Get convention
    if args.phase_convention == 'CASA':
        uvw = -(ms.UVW.data.astype(np.float64))
    elif args.phase_convention == 'CODEX':
        uvw = ms.UVW.data.astype(np.float64)
    else:
        raise ValueError("Unknown sign convention for phase")

    # Get rest of dimensions
    n_row, n_freq, n_corr = flag.shape

    # Raise error if correlation axis too small
    if n_corr != 4:
        raise NotImplementedError("Only 4 correlations "\
            + "currently supported")

    # Get phase direction
    radec0_table = xds_from_table(args.ms+'::FIELD')[0]
    radec0 = radec0_table.PHASE_DIR.data.squeeze().compute()
    
    # Get frequency column
    freq_table = xds_from_table(args.ms+'::SPECTRAL_WINDOW')[0]
    freq = freq_table.CHAN_FREQ.data.astype(np.float64)[0]

    # Check dimension
    assert freq.size == n_freq

    # Check for sky-model
    if args.sky_model == 'MODEL-1.txt':
        args.sky_model = MODEL_1
    elif args.sky_model == 'MODEL-4.txt':
        args.sky_model = MODEL_4
    elif args.sky_model == 'MODEL-50.txt':
        args.sky_model = MODEL_50
    else:
        raise ValueError(f"Sky-model {args.sky_model} not in "\
            + "kalcal/datasets/sky_model/")

    # Build source model from lsm
    lsm = Tigger.load(args.sky_model)

    # Direction axis
    n_dir = len(lsm.sources)

    # Create initial coordinate array and source names
    lm = np.zeros((n_dir, 2), dtype=np.float64)

    # Cycle coordinates creating a source with flux
    for d, source in enumerate(lsm.sources):

        # Extract position
        radec_s = np.array([[source.pos.ra, source.pos.dec]])
        lm[d] =  radec_to_lm(radec_s, radec0)

    # Generate gains
    jones = None
    print('==> Jones-only mode')
    if args.mode == "phase":
        jones = phase_gains(lm, freq, n_time, n_ant, args.alpha_std)

    elif args.mode == "normal":
        jones = normal_gains(tbin_idx, freq, lm, n_ant, n_corr, 
                    args.sigma_f, args.lt, args.lnu, args.ls)
    else:
        raise ValueError("Only normal and phase modes available.")

    # Reduce jones to diagonals only
    jones = jones[:, :, :, :, (0, -1)]

    # Jones to complex
    jones = jones.astype(np.complex128)

    # Generate filename
    if args.out == "":
        args.out = f"{args.mode}.npy"
  
    # Save gains and settings to file
    with open(args.out, 'wb') as file:        
        np.save(file, jones)

    print(f"==> Created Jones data: {args.out}")


def data(args):
    """Generate model data only, using a giving 
    measurement set and linked jones matrix."""

     # Set thread count to cpu count
    if args.ncpu:
        from multiprocessing.pool import ThreadPool
        import dask
        dask.config.set(pool=ThreadPool(args.ncpu))
    else:
        import multiprocessing
        args.ncpu = multiprocessing.cpu_count()

    # Get full time column and compute row chunks
    ms = xds_from_table(args.ms)[0]
   
    row_chunks, tbin_idx, tbin_counts = chunkify_rows(
        ms.TIME, args.utimes_per_chunk)
    
    # Convert time rows to dask arrays
    tbin_idx = da.from_array(tbin_idx, 
                 chunks=(args.utimes_per_chunk))
    tbin_counts = da.from_array(tbin_counts, 
                    chunks=(args.utimes_per_chunk))

    # Time axis
    n_time = tbin_idx.size

    # Get antenna columns
    ant1 = ms.ANTENNA1.data
    ant2 = ms.ANTENNA2.data

    # No. of antennas axis
    n_ant = (np.maximum(ant1.max(), ant2.max()) + 1).compute()
    
    # Get flag column
    flag = ms.FLAG.data

    # Get convention
    if args.phase_convention == 'CASA':
        uvw = -(ms.UVW.data.astype(np.float64))
    elif args.phase_convention == 'CODEX':
        uvw = ms.UVW.data.astype(np.float64)
    else:
        raise ValueError("Unknown sign convention for phase")

    # Get rest of dimensions
    n_row, n_freq, n_corr = flag.shape

    # Raise error if correlation axis too small
    if n_corr != 4:
        raise NotImplementedError("Only 4 correlations "\
            + "currently supported")

    # Get phase direction
    radec0_table = xds_from_table(args.ms+'::FIELD')[0]
    radec0 = radec0_table.PHASE_DIR.data.squeeze().compute()

    # Get frequency column
    freq_table = xds_from_table(args.ms+'::SPECTRAL_WINDOW')[0]
    freq = freq_table.CHAN_FREQ.data.astype(np.float64)[0]

    # Check dimension
    assert freq.size == n_freq

    # Check for sky-model
    if args.sky_model == 'MODEL-1.txt':
        args.sky_model = MODEL_1
    elif args.sky_model == 'MODEL-4.txt':
        args.sky_model = MODEL_4
    elif args.sky_model == 'MODEL-50.txt':
        args.sky_model = MODEL_50
    else:
        raise ValueError(f"Sky-model {args.sky_model} not in "\
            + "kalcal/datasets/sky_model/")

    # Build source model from lsm
    lsm = Tigger.load(args.sky_model)

    # Direction axis
    n_dir = len(lsm.sources)

    # Create initial model array
    model = np.zeros((n_dir, n_freq, n_corr), dtype=np.float64)

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

    # Retrieve gains
    jones = None        
    if args.out == '':
        args.out = f"{args.mode}.npy"

    with open(args.out, 'rb') as file:
        jones = np.load(file)

    jones_shape = jones.shape

    # Build dask graph
    lm = da.from_array(lm, chunks=lm.shape)
    model = da.from_array(model, chunks=model.shape)
    jones_da = da.from_array(jones, chunks=(args.utimes_per_chunk,)
                            + jones_shape[1::])    

    # Append antenna columns
    cols = []
    cols.append('ANTENNA1')
    cols.append('ANTENNA2')
    cols.append('UVW')

    # Load data in in chunks and apply gains to each chunk
    xds = xds_from_ms(args.ms, columns=cols, 
            chunks={"row": row_chunks})[0]
    ant1 = xds.ANTENNA1.data
    ant2 = xds.ANTENNA2.data

    # Adjust UVW based on phase-convention
    if args.phase_convention == 'CASA':
        uvw = -xds.UVW.data.astype(np.float64)
    elif args.phase_convention == 'CODEX':
        uvw = xds.UVW.data.astype(np.float64)
    else:
        raise ValueError("Unknown sign convention for phase")
    

    # Get model visibilities
    model_vis = np.zeros((n_row, n_freq, n_dir, n_corr), 
                            dtype=np.complex128)    
    
    for s in range(n_dir):
        model_vis[:, :, s] = im_to_vis(
            model[s].reshape((1, n_freq, n_corr)),
            uvw, 
            lm[s].reshape((1, 2)), 
            freq, 
            dtype=np.complex64, convention='fourier')

    # NP to Dask
    model_vis = da.from_array(model_vis, chunks=(row_chunks, 
                                n_freq, n_dir, n_corr))

    # Convert Stokes to corr
    in_schema = ['I', 'Q', 'U', 'V']
    out_schema = [['RR', 'RL'], ['LR', 'LL']]
    model_vis = convert(model_vis, in_schema, out_schema)

    # Apply gains
    data = corrupt_vis(tbin_idx, tbin_counts, ant1, ant2,
                    jones_da, model_vis).reshape(
                        (n_row, n_freq, n_corr))
    
    # Assign model visibilities
    out_names = []
    for d in range(n_dir):
        xds = xds.assign(**{source_names[d]: 
                (("row", "chan", "corr"), 
                model_vis[:, :, d].reshape(
                    n_row, n_freq, n_corr).astype(np.complex64))})

        out_names += [source_names[d]]

    # Assign noise free visibilities to 'CLEAN_DATA'
    xds = xds.assign(**{'CLEAN_DATA': (("row", "chan", "corr"), 
            data.astype(np.complex64))})

    out_names += ['CLEAN_DATA']
    
    # Get noise realisation
    if args.sigma_n > 0.0:

        # Noise matrix
        noise = (da.random.normal(loc=0.0, scale=args.sigma_n, 
                    size=(n_row, n_freq, n_corr), 
                    chunks=(row_chunks, n_freq, n_corr)) \

                + 1.0j*da.random.normal(loc=0.0, scale=args.sigma_n, 
                    size=(n_row, n_freq, n_corr), 
                    chunks=(row_chunks, n_freq, n_corr)))/np.sqrt(2.0)

        # Zero matrix for off-diagonals
        zero = da.zeros_like(noise[:, :, 0])

        # Dask to NP
        noise = noise.compute()
        zero = zero.compute()

        # Remove noise on off-diagonals
        noise[:, :, 1] = zero[:, :]
        noise[:, :, 2] = zero[:, :]

        # NP to Dask
        noise = da.from_array(noise, chunks=(row_chunks, n_freq, n_corr))
        
        # Assign noise to 'NOISE'
        xds = xds.assign(**{'NOISE': (("row", "chan", "corr"), 
                noise.astype(np.complex64))})

        out_names += ['NOISE']

        # Add noise to data and assign to 'DATA'
        noisy_data = data + noise
        xds = xds.assign(**{'DATA': (("row", "chan", "corr"), 
                noisy_data.astype(np.complex64))})

        out_names += ['DATA']
        
    # Create a write to the table
    write = xds_to_table(xds, args.ms, out_names)

    # Submit all graph computations in parallel
    print('==> Data-only mode')
    with ProgressBar():
        write.compute()

    print(f"==> Applied Jones to MS: {args.ms} <--> {args.out}")


def both(args):
    """Generate model data, corrupted visibilities and 
    gains (phase-only or normal)"""
        
    # Set thread count to cpu count
    if args.ncpu:
        from multiprocessing.pool import ThreadPool
        import dask
        dask.config.set(pool=ThreadPool(args.ncpu))
    else:
        import multiprocessing
        args.ncpu = multiprocessing.cpu_count()

    # Get full time column and compute row chunks
    ms = xds_from_table(args.ms)[0]
   
    row_chunks, tbin_idx, tbin_counts = chunkify_rows(
        ms.TIME, args.utimes_per_chunk)
    
    # Convert time rows to dask arrays
    tbin_idx = da.from_array(tbin_idx, 
                 chunks=(args.utimes_per_chunk))
    tbin_counts = da.from_array(tbin_counts, 
                    chunks=(args.utimes_per_chunk))

    # Time axis
    n_time = tbin_idx.size

    # Get antenna columns
    ant1 = ms.ANTENNA1.data
    ant2 = ms.ANTENNA2.data

    # No. of antennas axis
    n_ant = (np.maximum(ant1.max(), ant2.max()) + 1).compute()

    # Get flag column
    flag = ms.FLAG.data

    # Get convention
    if args.phase_convention == 'CASA':
        uvw = -(ms.UVW.data.astype(np.float64))
    elif args.phase_convention == 'CODEX':
        uvw = ms.UVW.data.astype(np.float64)
    else:
        raise ValueError("Unknown sign convention for phase")
        
    # Get rest of dimensions
    n_row, n_freq, n_corr = flag.shape

    # Raise error if correlation axis too small
    if n_corr != 4:
        raise NotImplementedError("Only 4 correlations "\
            + "currently supported")

    # Get phase direction
    radec0_table = xds_from_table(args.ms+'::FIELD')[0]
    radec0 = radec0_table.PHASE_DIR.data.squeeze().compute()

    # Get frequency column
    freq_table = xds_from_table(args.ms+'::SPECTRAL_WINDOW')[0]
    freq = freq_table.CHAN_FREQ.data.astype(np.float64)[0]

    # Check dimension
    assert freq.size == n_freq

    # Check for sky-model
    if args.sky_model == 'MODEL-1.txt':
        args.sky_model = MODEL_1
    elif args.sky_model == 'MODEL-4.txt':
        args.sky_model = MODEL_4
    elif args.sky_model == 'MODEL-50.txt':
        args.sky_model = MODEL_50
    else:
        raise NotImplemented(f"Sky-model {args.sky_model} not in "\
            + "kalcal/datasets/sky_model/")

    # Build source model from lsm
    lsm = Tigger.load(args.sky_model)

    # Direction axis
    n_dir = len(lsm.sources)

    # Create initial model array
    model = np.zeros((n_dir, n_freq, n_corr), dtype=np.float64)

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

    # Generate gains
    jones = None
    jones_shape = None

    # Dask to NP
    t = tbin_idx.compute()
    nu = freq.compute()

    print('==> Both-mode')
    if args.mode == "phase":
        jones = phase_gains(lm, nu, n_time, n_ant, args.alpha_std)

    elif args.mode == "normal":
        jones = normal_gains(t, nu, lm, n_ant, n_corr, 
                    args.sigma_f, args.lt, args.lnu, args.ls)
    else:
        raise ValueError("Only normal and phase modes available.")
    
    print()
    # Reduce jones to diagonals only
    jones = jones[:, :, :, :, (0, -1)]

    # Jones to complex
    jones = jones.astype(np.complex128)

    # Jones shape
    jones_shape = jones.shape

    # Generate filename
    if args.out == "":
        args.out = f"{args.mode}.npy"

    # Save gains and settings to file
    with open(args.out, 'wb') as file:        
        np.save(file, jones)

    # Build dask graph
    lm = da.from_array(lm, chunks=lm.shape)
    model = da.from_array(model, chunks=model.shape)
    jones_da = da.from_array(jones, chunks=(args.utimes_per_chunk,)
                            + jones_shape[1::])    

    # Append antenna columns
    cols = []
    cols.append('ANTENNA1')
    cols.append('ANTENNA2')
    cols.append('UVW')

    # Load data in in chunks and apply gains to each chunk
    xds = xds_from_ms(args.ms, columns=cols, 
            chunks={"row": row_chunks})[0]
    ant1 = xds.ANTENNA1.data
    ant2 = xds.ANTENNA2.data

    # Adjust UVW based on phase-convention
    if args.phase_convention == 'CASA':
        uvw = -xds.UVW.data.astype(np.float64)       
    elif args.phase_convention == 'CODEX':
        uvw = xds.UVW.data.astype(np.float64)
    else:
        raise ValueError("Unknown sign convention for phase")
    

    # Get model visibilities
    model_vis = np.zeros((n_row, n_freq, n_dir, n_corr), 
                            dtype=np.complex128)    

    for s in range(n_dir):
        model_vis[:, :, s] = im_to_vis(
            model[s].reshape((1, n_freq, n_corr)),
            uvw, 
            lm[s].reshape((1, 2)), 
            freq, 
            dtype=np.complex64, convention='fourier')

    # NP to Dask
    model_vis = da.from_array(model_vis, chunks=(row_chunks, 
                                n_freq, n_dir, n_corr))

    # Convert Stokes to corr
    in_schema = ['I', 'Q', 'U', 'V']
    out_schema = [['RR', 'RL'], ['LR', 'LL']]
    model_vis = convert(model_vis, in_schema, out_schema)

    # Apply gains
    data = corrupt_vis(tbin_idx, tbin_counts, ant1, ant2,
                    jones_da, model_vis).reshape(
                        (n_row, n_freq, n_corr))
    
    # Assign model visibilities
    out_names = []
    for d in range(n_dir):
        xds = xds.assign(**{source_names[d]: 
                (("row", "chan", "corr"), 
                model_vis[:, :, d].reshape(
                    n_row, n_freq, n_corr).astype(np.complex64))})

        out_names += [source_names[d]]

    # Assign noise free visibilities to 'CLEAN_DATA'
    xds = xds.assign(**{'CLEAN_DATA': (("row", "chan", "corr"), 
            data.astype(np.complex64))})

    out_names += ['CLEAN_DATA']
    
    # Get noise realisation
    if args.sigma_n > 0.0:

        # Noise matrix
        noise = (da.random.normal(loc=0.0, scale=args.sigma_n, 
                    size=(n_row, n_freq, n_corr), 
                    chunks=(row_chunks, n_freq, n_corr)) \

                + 1.0j*da.random.normal(loc=0.0, scale=args.sigma_n, 
                    size=(n_row, n_freq, n_corr), 
                    chunks=(row_chunks, n_freq, n_corr)))/np.sqrt(2.0)

        # Zero matrix for off-diagonals
        zero = da.zeros_like(noise[:, :, 0])

        # Dask to NP
        noise = noise.compute()
        zero = zero.compute()

        # Remove noise on off-diagonals
        noise[:, :, 1] = zero[:, :]
        noise[:, :, 2] = zero[:, :]

        # NP to Dask
        noise = da.from_array(noise, chunks=(row_chunks, n_freq, n_corr))
        
        # Assign noise to 'NOISE'
        xds = xds.assign(**{'NOISE': (("row", "chan", "corr"), 
                noise.astype(np.complex64))})

        out_names += ['NOISE']

        # Add noise to data and assign to 'DATA'
        noisy_data = data + noise
        xds = xds.assign(**{'DATA': (("row", "chan", "corr"), 
                noisy_data.astype(np.complex64))})

        out_names += ['DATA']
        
    # Create a write to the table
    write = xds_to_table(xds, args.ms, out_names)

    # Submit all graph computations in parallel
    with ProgressBar():
        write.compute()

    print(f"==> Applied Jones to MS: {args.ms} <--> {args.out}")