# siglab_lib/scatterPlot.py
import os
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def create_higuchi_scatter(app):
    """
    Create a scatter plot of Higuchi Mean vs Slope, colored by state
    
    Parameters:
    - app: Main application instance
    """
    from siglab_lib.calcHiguchi import calculate_higuchi_stats
    from siglab_lib.calcStats import calculate_segment_stats
    
    # Calculate Higuchi and segment statistics
    higuchi_stats = calculate_higuchi_stats(app.magR, app.time_S)
    segment_stats = calculate_segment_stats(app)
    
    # Create scatter plot window
    plot_window = tk.Toplevel()
    plot_window.title(f"Higuchi Mean vs Slope: {os.path.basename(app.filepath)}")
    plot_window.geometry('800x600')
    plot_window.configure(bg='#B0C4DE')  # Match main window background
    
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#B0C4DE')
    ax.set_facecolor('#E6EDF3')
    
    # Create canvas
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    
    # Create toolbar
    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    
    # Pack widgets
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar.pack(side=tk.TOP, fill=tk.X)
    
    # Calculate Higuchi Mean and Slope
    higuchi_mean = np.mean(higuchi_stats[:, :5], axis=1)
    higuchi_slope = higuchi_stats[:, 5]
    
    # Plot scatter for each state
    for state_val, state_info in app.state_colors.items():
        # Find indices for this state
        state_mask = app.tag_state == state_val
        
        # Plot scatter for this state
        ax.scatter(
            higuchi_mean[state_mask], 
            higuchi_slope[state_mask], 
            color=state_info['color'], 
            label=state_info['name'],
            alpha=0.7
        )
    
    ax.set_title(f"Higuchi Mean vs Slope: {os.path.basename(app.filepath)}")
    ax.set_xlabel('Higuchi Mean')
    ax.set_ylabel('Higuchi Slope')
    ax.grid(True)
    ax.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Show the plot
    canvas.draw()

def create_range_bloodref_scatter(app):
    """
    Create a scatter plot of Range vs Blood Reference Difference, colored by state
    
    Parameters:
    - app: Main application instance
    """
    from siglab_lib.calcStats import calculate_segment_stats
    
    # Calculate segment statistics
    segment_stats = calculate_segment_stats(app)
    
    # Create scatter plot window
    plot_window = tk.Toplevel()
    plot_window.title(f"Range vs Blood Reference Diff: {os.path.basename(app.filepath)}")
    plot_window.geometry('800x600')
    plot_window.configure(bg='#B0C4DE')  # Match main window background
    
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#B0C4DE')
    ax.set_facecolor('#E6EDF3')
    
    # Create canvas
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    
    # Create toolbar
    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()
    
    # Pack widgets
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar.pack(side=tk.TOP, fill=tk.X)
    
    # Extract segment statistics
    segment_rng = segment_stats['segmentStats']['each'][:, 3]  # Range column
    
    # Calculate blood reference difference
    blood_est_val = segment_stats['bloodEstVal']
    segment_mean = segment_stats['segmentStats']['each'][:, 2]  # Mean column
    blood_ref_diff = np.abs(segment_mean - blood_est_val)
    
    # Plot scatter for each state
    for state_val, state_info in app.state_colors.items():
        # Find indices for this state
        state_mask = app.tag_state == state_val
        
        # Plot scatter for this state
        ax.scatter(
            segment_rng[state_mask], 
            blood_ref_diff[state_mask], 
            color=state_info['color'], 
            label=state_info['name'],
            alpha=0.7
        )
    
    ax.set_title(f"Range vs Blood Reference Diff: {os.path.basename(app.filepath)}")
    ax.set_xlabel('Range')
    ax.set_ylabel('Blood Reference Difference')
    ax.grid(True)
    ax.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Show the plot
    canvas.draw()