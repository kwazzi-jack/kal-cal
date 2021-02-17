from .plotops import gains_magnitude_time
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np

colors = ['black', 'red', 'blue', 'green', 'purple', 'teal']

def plot_time(
    *args, 
    index=(0,0,0),
    axis='real',
    title='',
    show=None):
    """Plot gains-magnitude value for each antenna q in, 
    g_p x g_q^*, where p is the reference antenna for each 
    jones data present in args."""

    # Get reference antenna
    ref = index[0]

    # If reference antenna not in show
    # list, add it
    if show != None and ref not in show:
        show.insert(ref, ref)

    # Convert tuple to list
    args = list(args)

    # Number of plots (x2)
    nplots = len(args)

    # Restrict which antennas to plot
    if show != None:
        for n in range(0, nplots, 3):
            args[n] = (args[n])[:, show]

    # Select first jones param
    jones = args[0]

    # Get number of antennas
    n_antennas = jones.shape[1]

    # Get number of time-steps
    time_steps = jones.shape[0]

    # Get time axis values
    times = np.arange(time_steps)    

    # Create figure and axes
    fig, axes = plt.subplots(n_antennas - 1, 
                                figsize=(16,12)) 

    # Set the figure title if present
    fig.suptitle(f"Gains-magnitude plot over time ({axis})\n"\
                + title, fontsize=16)

    # Adjuster to account for removing an antenna
    adj = 0

    # Part function
    if axis == 'real':
        axis = np.real
    elif axis == 'imag':
        axis = np.imag
    else:
        raise ValueError("Incorrect part selected - only real or imag")

    # Loop over each antenna (except reference antenna)
    # and create separate plot
    for ant in range(n_antennas):
        # Check if antenna is reference antenna
        if ant == ref:
            adj = 1
            continue
        
        # Select relevant antenna axis
        ax = axes[ant - adj]   

        # Generate label using p and q
        label = rf"$g_{{{ref}}} \times g_{{{ant}}}^*$"
        ax.set_ylabel(label, color='black')        

        # Plot each jones data present
        for n in range(0, nplots, 3):
            jones = args[n]
            name = args[n + 1]
            line = args[n + 2]
            aindex = (ant,) + index[1:3]
            i = (n//2) % len(colors)
            pq = axis(gains_magnitude_time(jones, aindex, ref))
            ax.plot(times, pq, line, color=colors[i], 
                        label=name, lw=1.2)
            ax.tick_params(axis='x')
            ax.tick_params(axis='y') 
        # If first plot, add legend to top plot    
        if ant - adj == 0:
            ax.legend(facecolor='white', markerscale=2.5, loc='upper left',
                            ncol=nplots//2, mode="expand")

        # If last antenna to plot, show x-label
        if ant - adj == n_antennas - 2:
            ax.set_xlabel('Time-steps', color='black')