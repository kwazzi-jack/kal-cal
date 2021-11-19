#!/usr/bin/bash

# NOTE Might have to given execute permissions for this file. You can do so
# with the following

#       chmod +x full_pipeline.sh


# Make a MeerKAT measurement set
kal-create ms --yaml create_ms.yml meerkat.ms

# Make gains for the measurement set
kal-create gains --yaml create_gains.yml meerkat.ms skymodel.txt

# Generate visibilities for the measurement set with gains
kal-create data --yaml create_data.yml meerkat.ms skymodel.txt true_gains.npy

# Calibrate the noisy corrupted gains
kal-calibrate vanilla --yaml calibrate_vanilla.yml meerkat.ms

# Plot results of calibration against true gains as a gains-product plot
kal-plot gains --yaml plot_gains.yml