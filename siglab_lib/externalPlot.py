# siglab_lib/externalPlot.py
import os
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def create_stats_plot(app):
    """
    Create a plot of segment statistics in a new window
    
    Parameters:
    - app: Main application instance
    """
    # Use the pre-calculated stats from the app instance
    if not hasattr(app, 'stats') or app.stats is None:
        tk.messagebox.showinfo("Stats Plot", "No stats available. Calculate stats first.")
        return
    
    stats_data = app.stats
    #print("bloodEstVal:", *[int(val) for val in stats_data['bloodEstVal'][:30]])
    #print("bloodEstRng:", *[int(val) for val in stats_data['bloodEstRng'][:30]])
    
    # Rest of the plotting code remains the same
    # Create new top-level window
    plot_window = tk.Toplevel()
    plot_window.title(f"MinMaxRng plot: {os.path.basename(app.filepath)}")
    plot_window.geometry('1000x600')
    
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create canvas WITH explicit interactive mode
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()  # Important: call draw before creating toolbar
    
    # Create toolbar
    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    
    # Pack widgets in specific order
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar.pack(side=tk.TOP, fill=tk.X)
    
    # Extract segment stats data
    segment_stats = stats_data['segmentStats']['each']
    tag_time_S = stats_data['segmentStats']['time']
    
    # Extract blood estimate values
    blood_est_val = stats_data['bloodEstVal']
    
    # Plot data
    ax.scatter(tag_time_S, segment_stats[:, 2], color='black', label='Mean', s=30)
    
    # Plot min-max range lines
    for i in range(len(tag_time_S)):
        ax.vlines(tag_time_S[i], segment_stats[i, 1], segment_stats[i, 0], 
                  color='blue', alpha=0.5, linewidth=2)
    
    # Plot blood estimate value as a horizontal red line
    #ax.axhline(y=blood_est_val[0], color='red', linestyle='--', label='Blood Est Value')
    ax.plot(tag_time_S, blood_est_val, color='darkred', linestyle='-', label='Blood Est Value')
    
    ax.set_title(f"MinMaxRng plot: {os.path.basename(app.filepath)}")
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Magnitude')
    ax.legend()
    ax.grid(True)
    
    # Show the plot
    canvas.draw()
#-------------------------------------------------------------
#                    create_higuchi_plot
#-------------------------------------------------------------
def create_higuchi_plot(app):
    """
    Create plots of Higuchi Fractal Dimension statistics
    
    Parameters:
    - app: Main application instance
    """
    from siglab_lib.calcHiguchi import calculate_higuchi_stats
    
    # Calculate Higuchi statistics
    higuchi_stats = calculate_higuchi_stats(app.magR, app.time_S)
    
    # Create new top-level window 
    plot_window = tk.Toplevel()
    plot_window.title(f"Higuchi Fractal Dimension: {os.path.basename(app.filepath)}")
    plot_window.geometry('1000x600')
    plot_window.configure(bg='#B0C4DE')  # Match main window background
    
    # Create matplotlib figure with two subplots
    fig, (mean_ax, slope_ax) = plt.subplots(2, 1, figsize=(10, 6), height_ratios=[1, 1], sharex=True)
    
    # Set figure background to match main window
    fig.patch.set_facecolor('#B0C4DE')
    
    # Set axes background to match plot area in main window
    mean_ax.set_facecolor('#E6EDF3')
    slope_ax.set_facecolor('#E6EDF3')
    
    # Create canvas WITH explicit interactive mode
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()  # Important: call draw before creating toolbar
    
    # Create toolbar
    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    
    # Pack widgets in specific order
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar.pack(side=tk.TOP, fill=tk.X)
    
    # Extract time points
    tag_time_S = app.time_S[::30]  # Time points for each segment
    
    # Calculate 1-second mean of Higuchi values
    higuchi_mean = np.mean(higuchi_stats[:, :5], axis=1)
    
    # Plot Higuchi Mean with 1 pt width line and 10pt dots
    mean_ax.plot(tag_time_S, higuchi_mean, color='black', linewidth=1.0)
    mean_ax.scatter(tag_time_S, higuchi_mean, color='black', s=10)
    mean_ax.set_title(f"Higuchi Mean: {os.path.basename(app.filepath)}")
    mean_ax.set_ylabel('Higuchi Mean')
    mean_ax.grid(True)
    
    # Plot Higuchi Slope with dots only
    slope_ax.scatter(tag_time_S, higuchi_stats[:, 5], color='black', s=10)
    slope_ax.set_title(f"Higuchi Slope: {os.path.basename(app.filepath)}")
    slope_ax.set_xlabel('Time (s)')
    slope_ax.set_ylabel('Higuchi Slope')
    slope_ax.grid(True)
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Show the plot
    canvas.draw()