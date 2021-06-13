import numpy as np
from omegaconf import OmegaConf as ocf
import matplotlib.pyplot as plt
plt.style.use('ggplot')


def gains(**kwargs):
    """Plot gains-magnitude value for each antenna q in, 
    g_p x g_q^*, where p is the reference antenna for each 
    jones data present in args."""

    # Options to attributed dictionary
    if kwargs["yaml"] is not None:
        options = ocf.load(kwargs["yaml"])
    else:    
        options = ocf.create(kwargs)    

    # Set to struct
    ocf.set_struct(options, True)

    # Get show list
    show = options.show.replace(" ", "").split(",")
    show = list(map(int, show))

    # If reference antenna not in show
    # list, add it
    if -1 not in show and options.ref_ant not in show:
        show.append(options.ref, options.ref)

    # Number of plots
    nplots = len(options.plot)

    # List for all plots
    plots = []

    # Open all gains files and put in dictionaries
    for plot in options.plot:
        # Extract details
        filename, label, color, linestyle = plot

        # Open gains files
        with open(filename, "rb") as file:
            jones = np.load(filename)

        # Restrict to plots to show 
        if -1 not in show:
            jones = jones[:, show]

        # Plot dictionary
        plots.append({
            "jones"     : jones,
            "label"     : label,
            "color"     : color,
            "linestyle" : linestyle
        })     

    # Get dimensions
    n_time, n_ant, n_chan = plots[0]["jones"].shape[0:3]

    # Change show if -1 to all
    if -1 in show:
        show = np.arange(n_ant)

    # Create figure and axes
    fig, axes = plt.subplots(n_ant - 1, figsize=(16,12)) 

    # Set the figure title if present
    if options.title is not None:
        fig.suptitle(options.title, fontsize=16)
    else:
        fig.suptitle(f"Gains magnitude plot over {options.axis.upper()} "\
                    + f"({options.complex_axis.upper()})",
                        fontsize=16)

    # Adjuster to account for removing an antenna
    adj = 0

    # Part function
    if options.complex_axis.lower() == 'real':
        set_axis = np.real
    elif options.complex_axis.lower() == 'imag':
        set_axis = np.imag
    else:
        raise ValueError("Incorrect part selected - only real or imag")

    # Set x-axis to time or frequency
    if options.axis.lower() == 'time':
        x_axis = np.arange(n_time)
    elif options.axis.lower() == 'freq':
        x_axis = np.arange(n_chan)
    else:
        raise ValueError('Unknown x-axis selected.')

    # Loop over each antenna (except reference antenna)
    # and create separate plot
    for i, ant in zip(show, range(n_ant)):
        # Check if antenna is reference antenna
        if ant == options.ref_ant:
            adj = 1
            continue
        
        # Select relevant antenna axis
        ax = axes[ant - adj]   

        # Generate label using p and q
        if options.complex_axis.lower() == 'real':
            y_label = rf"$\Re\{{g_{{{i}}} \times g_{{{options.ref_ant}}}^*\}}$"
        elif options.complex_axis.lower() == 'imag':
            y_label = rf"$\Im\{{g_{{{i}}} \times g_{{{options.ref_ant}}}^*\}}$"
        else:
            raise ValueError("Incorrect part selected - only real or imag")

        ax.set_ylabel(y_label, color='black')        

        # Plot each jones data present
        for n in range(0, nplots):
            plot = plots[n]
            # This works because I'm assuming:
            # true_jones.shape = (n_time, n_ant, n_chan, n_dir, n_corr)
            # kalman_jones.shape = (n_time, n_ant, n_chan, n_dir, n_aug)
            jones = plot["jones"][:, :, :, :, 0]
            label = plot["label"]
            color = plot["color"]
            linestyle = plot["linestyle"]

            # Get g_p x g_q^* either from time or freq axis
            if options.axis.lower() == "time":
                pq = jones[:, ant, 0, 0] * jones[:, options.ref_ant, 0, 0].conj() 
                
            elif options.axis.lower() == "freq":
                pq = jones[0, ant, :, 0] * jones[0, options.ref_ant, :, 0].conj() 
                pq = set_axis(pq)

            # Choose real or imaginary
            pq = set_axis(pq)
            ax.plot(x_axis, pq, linestyle=linestyle, color=color, label=label, lw=1.2)
            ax.tick_params(axis='x')
            ax.tick_params(axis='y') 

        # If first plot, add legend to top plot    
        if ant - adj == 0:
            ax.legend(facecolor='white', markerscale=2.5, loc='upper left',
                            ncol=nplots, mode="expand")

        # If last antenna to plot, show x-label
        if ant - adj == n_ant - 2:
            ax.set_xlabel(f'{options.axis.upper()}-STEPS', color='black')

    # Save plot
    if options.out_file is None:
        plt.savefig("gains_plot.png")
    else:
        plt.savefig(options.out_file)

    # Show plot
    if options.display:
        plt.show()