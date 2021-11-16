from kalcal.create import ms, gains, data
from kalcal.calibration import vanilla
from kalcal.plotting import plot


def main():
    # Names of input-files
    ms_name = "meerkat.ms"
    skymodel_name = "skymodel.txt"
    gains_name = "true_gains.npy"

    # Create ms options
    ms_options = {
        "tel"               : "meerkat",
        "pos_type"          : "ascii",
        "dec"               : "-30d14m50s",
        "ra"                : "11h49m15s",
        "synthesis"         : 2,
        "dtime"             : 10,
        "freq0"             : "1GHz",
        "nchan"             : "1",
        "dfreq"             : "1MHz",
        "stokes"            : "XX XY YX YY",
        "yaml"              : None
    }

    # Create a new measurement set using simms
    ms.new(ms_name, **ms_options)

    # Create gains options
    gains_options = {
        "type"              : "normal",
        "std"               : 0.2,
        "diffs"             : [0.02, 0.05, 0.5],
        "die"               : True,
        "out_file"          : gains_name,
        "yaml"              : None
    }

    # Create a new amplitude-only gains
    gains.new(ms_name, skymodel_name, **gains_options)

    # Create data options
    data_options = {
        "std"               : 1.0,
        "phase_convention"  : "CODEX",
        "die"               : True,
        "utime"             : 30,
        "ncpu"              : 8,
        "mname"             : "MODEL_DATA",
        "dname"             : "DATA",
        "yaml"              : None
    }

    # Create model data and corrupted visibilities using ms and gains
    data.new(ms_name, skymodel_name, gains_name, **data_options)

    # Vanilla calibrate options
    cal_options = {
        "filter"            : 1,
        "smoother"          : 1,
        "algorithm"         : "NUMBA",
        "sigma_f"           : 0.0075,
        "sigma_n"           : 1.0,
        "step_control"      : 0.5,
        "model_column"      : "MODEL_DATA",
        "vis_column"        : "DATA",
        "weight_column"     : "WEIGHT",
        "out_filter"        : "filter.npy",
        "out_smoother"      : "smoother.npy",
        "out_data"          : "", # Not using corrected data
        "out_weight"        : "", # Not using imaging weights
        "ncpu"              : 8, 
        "yaml"              : None
    }
    
    # Run vanilla calibrate
    vanilla.calibrate(ms_name, **cal_options)

    # Plots to show (file, label, color, line-style)
    plots = [
        ["true_gains.npy", "True Jones", "black", "-"],
        ["filter.npy", "EKF", "red", "."],
        ["smoother.npy", "EKS", "green", "-"]
    ]

    # Plot gains options
    plot_options = {
        "plot"              : plots,
        "ref_ant"           : 0,
        "show"              : "0, 1, 2, 3",
        "axis"              : "TIME",
        "complex_axis"      : "REAL",
        "title"             : "Gains magnitude over TIME (REAL)",
        "out_file"          : "gains_plot.png",
        "display"           : True,
        "yaml"              : None
    }

    # Run plot gains
    plot.gains(**plot_options)


if __name__ == "__main__":
    main()