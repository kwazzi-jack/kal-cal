#!/usr/bin/bash

# NOTE Might have to given execute permissions for this file. You can do so
# with the following

#       chmod +x full_pipeline.sh


# Make a MeerKAT measurement set
kal-create ms --tel 'meerkat' --pos_type 'ascii' --dec '-30d14m50s' --ra '11h49m15s' --synthesis 2 --dtime 10 --freq0 "1GHz" --nchan "1" --dfreq "1MHz" --stokes "XX XY YX YY" meerkat.ms

# Make gains for the measurement set
kal-create gains --type normal --std 0.2 --diffs 0.02 0.05 0.5 --die --out_file true_gains.npy meerkat.ms skymodel.txt

# # Generate visibilities for the measurement set with gains
kal-create data --std 1.0 --phase_convention CODEX --die --utime 30 --ncpu 8 --mname MODEL_DATA --dname DATA meerkat.ms skymodel.txt true_gains.npy

# Calibrate the noisy corrupted gains
kal-calibrate vanilla --filter 1 --smoother 1 --algorithm NUMBA --sigma-f 0.0075 --sigma-n 1.0 --step-control 0.5 --model-column MODEL_DATA --vis-column DATA --weight-column WEIGHT --out-filter filter.npy --out-smoother smoother.npy --out-data "" --out-weight "" --ncpu 8 meerkat.ms

# For plotting results, would suggest using a yaml file instead