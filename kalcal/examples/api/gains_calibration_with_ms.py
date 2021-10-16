from kalcal.calibration import vanilla
from kalcal.plotting import plot


def main():
    # Name of measurement set
    ms = "KAT7.MS"

    # Vanilla calibrate options
    cal_options = {
        "filter"        : 1,
        "smoother"      : 1,
        "algorithm"     : "NUMBA",
        "sigma_f"       : 0.005,
        "sigma_n"       : 1.0,
        "step_control"  : 0.5,
        "model_column"  : "MODEL_DATA",
        "vis_column"    : "DATA",
        "weight_column" : "WEIGHT",
        "out_filter"    : "filter.npy",
        "out_smoother"  : "smoother.npy",
        "out_data"      : "CORRECTED_DATA",
        "out_weight"    : "WEIGHT_SPECTRUM",
        "ncpu"          : 8, 
        "yaml"          : None
    }
    
    # Run vanilla calibrate
    vanilla.calibrate(ms, **cal_options)

    # Plots to show
    plots = [
        ["true_gains.npy", "True Jones", "black", "-"],
        ["filter.npy", "EKF", "red", ":"],
        ["smoother.npy", "EKS", "green", "-"]
    ]

    # Plot gains options
    plot_options = {
        "plot"         : plots,
        "ref_ant"      : 0,
        "show"         : "0, 1, 2, 3",
        "axis"         : "TIME",
        "complex_axis" : "REAL",
        "title"        : "Gains magnitude over TIME (REAL)",
        "out_file"     : "gains_plot.png",
        "display"      : True,
        "yaml"         : None
    }

    # Run plot gains
    plot.gains(**plot_options)


if __name__ == "__main__":
    main()