# Calibration via `kal-cal` command-line

`kal-cal` also implements some algorithms off the bat to be used without having to mess around with the library:

- `kal-create` - used to create measurement sets, gains, and visibilities,
- `kal-calibrate` - calls on calibration algorithms to be used on a given measurement set,
- `kal-plot` - plot results of the calibration from the measurement sets and gains files,
- `kalcal` - pipeline command that can run multiple commands of the above based on a config file.

Below is a pipeline you can use to test DI-calibration (DD-calibration is a WIP) for the MeerKAT array. It comes in three versions:

1. `bash` - to demonstrate command-line use,
2. `yaml` - to demonstrate use with config `yaml` files,
3. `kalcal` - to demonstrate a pipeline use with `kalcal`



## 1. `bash`

| **NOTE**: See `bash` dir for examples of the following


- Simulate a measurement set using `simms` via `kal-create`:

```[bash]
kal-create ms [OPTIONS] MSNAME
```
> Be aware that even though it uses `simms`, not all functionality of `simms` is in place in this function so if you wish to utilize more options, then rather uses `simms` itself. This function was merely created to automate antenna table selection.

- Simulate gains for the given measurement set via `kal-create`:

```[bash]
kal-create gains [OPTIONS] MS SKY_MODEL
```

- Simulate visibilities for the given measurement set using gains via `kal-create`:

```[bash]
kal-create data [OPTIONS] MS SKY_MODEL GAINS
```
> Utilizes `dask` and `dask-ms` to compute all of this for a speed-up so pay attention to the `ncpu` option as the default will use all cores.

- Calibrate over noisy corrupted visibilities via `kal-calibrate`:

```[bash]
kal-calibrate vanilla [OPTIONS] MS
```

- Plot results as a gains-product plot via `kal-plot`:

```[bash]
kal-plot gains [OPTIONS]
```

## 2. `yaml`

| **NOTE**: See `yaml` dir for examples of the following

This is simular to the `bash` commands, but here we insert all our options in a `yaml` file. All you do is set the option as a keyword and then its value. Be careful with options that have a hyphen, as this needs to be changed to a underscore for it to be recognized. Use the `-y` or `--yaml` option and point to the options file. Remember to also insert the arguments as well.

- Simulate a measurement set using `simms` via `kal-create`:

```[bash]
kal-create ms --yaml options_file.yml MSNAME
```

- Simulate gains for the given measurement set via `kal-create`:

```[bash]
kal-create gains --yaml options_file.yml MS SKY_MODEL
```

- Simulate visibilities for the given measurement set using gains via `kal-create`:

```[bash]
kal-create data --yaml options_file.yml MS SKY_MODEL GAINS
```

- Calibrate over noisy corrupted visibilities via `kal-calibrate`:

```[bash]
kal-calibrate vanilla --yaml options_file.yml MS
```

- Plot results as a gains-product plot via `kal-plot`:

```[bash]
kal-plot gains --yaml options_file.yml
```

## 3. `kalcal`

| **NOTE**: See `kalcal` dir for examples of the following

This command takes in a single `yaml` file with the following format:
```[yaml]
1:                              # <-- Unique ID for this command
  command: "kal-create ms"      # <-- Command to use in kal-cal suite (see bash section)
  arguments:                    # <-- Command arguments section (required)
    msname: "MEERKAT.MS"
  options:                      # <-- Command options section
    tel: 'meerkat'
    pos_type: 'ascii'
    dec: '-30d16m41s' 
    ra: '11h49m36s'    
    synthesis: 2
    dtime: 10
    freq0: "1GHz"
    nchan: "1"
    dfreq: "1MHz"
    stokes: "XX XY YX YY"
```

To run this pipeline of commands, simply run:
```[bash]
kalcal pipeline_file.yml
```

Some notes for the formatting of the `yaml` file:
- The ID needs to be a unique positive integer. Duplicates will raise an error.
- The command needs to point to a specific command and subcommand in `kal-cal` .
> See top of this page for list of available commands and use the `--help` option to see specific subcommands.
- The `command` keyword is always required.
- The `arguments` keyword is required when the subcommand takes in arguments.
- The `options` keyword is optional.

See `full_pipeline.yml` for a full example.