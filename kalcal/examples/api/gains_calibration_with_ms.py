from kalcal.calibration import vanilla
from kalcal.plotting import plot

def main():
    # Name of measurement set
    ms = "KAT7.MS"

    # Vanilla calibrate options
    cal_options = {
        "filter"        : 1,
        "smoother"      : 3,
        "algorithm"     : "NUMBA",
        "sigma_f"       : 1.0,
        "sigma_n"       : 0.1,
        "step_control"  : 0.5,
        "model_column"  : "J0",
        "vis_column"    : "DATA",
        "weight_column" : "WEIGHT",
        "out_file"      : "gains.npy",
        "which_gains"   : "BOTH",
        "yaml"          : None
    }
    
    # Run vanilla calibrate
    vanilla.calibrate(ms, **cal_options)

    # Plots to show
    plots = [
        ["normal_gains.npy", "True Jones", "black", "-"],
        ["filter_gains.npy", "EKF", "red", ":"],
        ["smoother_gains.npy", "EKS", "green", "-"]
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