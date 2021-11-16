# Calibration via `kal-cal` api

To utilize `kal-cal` in your `python` script, you will need the following:

1. `kalcal` package to use the api,
2. A CASA measurement set,
3. (Optional) A sky-model to simulate with,
4. (Optional) `simms` installed via `apt` and `pip` for creating a measurement set.

**NOTE**: A full example on how to use `kal-cal` api can be found in `gains_calibration_with_ms.py`.**

Below is a pipeline you can use to test DI-calibration (DD-calibration is a WIP) for the MeerKAT array. It starts simulating the measurement set, direction-independent gains to corrupt the visibilities, and the model and visibility data.

## 1. Simulation

`kal-cal` comes with its own simple suite of simulation tools to generate measurement sets, gains and visibilities to apply our calibration on. To start, we need a measurement set.

```[python]
from kalcal.create import ms

# Options for measurement set
OPTIONS_FOR_MS = {...}

# Create measurement set
ms.new("NAME_OF_MS.MS", **OPTIONS_FOR_MS)

# Runs simms with the given configuration
```

This is only a feature of `kal-cal` to simplify `simms` for testing purposes and also to auto-select antenna-tables for you (which is currently not a feature of `simms`). Next we need gains.

```[python]
from kalcal.create import gains

# Options for gains
OPTIONS_FOR_GAINS = {...}

# Create gains
gains.new("NAME_OF_MS.MS", "SKYMODEL_NAME.txt", **OPTIONS_FOR_GAINS)

# Generates gains in CODEX format to fit the measurement set
```
Note, here it infers all the information it needs from the measurement set AND the skymodel you wish to use. Finally, we generate the data.

```[python]
from kalcal.create import data

# Options for data
OPTIONS_FOR_DATA = {...}

# Create data
data.new("NAME_OF_MS.MS", "SKYMODEL_NAME.txt", 
            "NAME_OF_GAINS.npy", **OPTIONS_FOR_DATA)

# From the measurement set and gains, creates and corrupts the visibilities 
# writes back to the measurement set, all via dask-ms.
```
To create our visibilities, it needs the measurement set, skymodel and newly created gains (in CODEX format) to generate model visibilities, corrupted visibilities and noisy corrupted visibilities. See `gains_calibration_with_ms.py` for examples the above.

With this, we have everything to calibrate.

## 2. Calibration

With the measurement set and visibilities in hand, all we need to do is pass it into one of our `kal-cal` calibration algorithms. Similar to the simulated snippets, we calibrate as follows:

```[python]
from kalcal.calibration import vanilla

# Options for calibration
OPTIONS_FOR_CALIBRATION = {...}

# Calibrate to find gains solutions
vanilla.calibrate("NAME_OF_MS.MS", **OPTIONS_FOR_CALIBRATION)

# Will calibrate to find solutions
```

See `gains_calibration_with_ms.py` for an example of the above. When this is complete, we can plot the gains-product to see how our algorithm has done.

## 3. Plotting

To plot, all that is needed is gains in numpy `.npy` format and configurations for the lines. We are going to create a gains-product plot.

```[python]
from kalcal.plotting import plot

# Plots to show (file, label, color, line-style)
plots = [
    ["true_gains.npy", "True Jones", "black", "-"],
    ["filter.npy", "EKF", "red", "."],
    ["smoother.npy", "EKS", "green", "-"]
]

# Options for plotting
OPTIONS_FOR_PLOTTING = {...}

# Plotting over multiple gains
plot.gains(**OPTIONS_FOR_CALIBRATION)

# Will save and display the gains-product plot
```

That is the entire calibration process via api. Tweak the `sigma_f` and `sigma_n` parameters in the calibration section to see different results. 