import os
import sys
import tkinter as tk
import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from siglab_lib.mainWinSupport import InteractionModes, ToolbarUtils

# Add library path
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, 'siglab_lib')
sys.path.insert(0, lib_path)

class SignalLab:
    def __init__(self, root):
        # Window setup
        self.root = root
        self.root.title("SignalLab")
        self.root.geometry('1400x900')
        self.root.configure(bg='#B0C4DE')

        # Data storage
        self.filepath = None
        self.magR = None
        self.time_S = None
        self.tag_state = None

        # State colors with updated order
        self.state_colors = {
            0: {'name': 'Unknown', 'color': 'gray', 'label_color': 'white'},
            1: {'name': 'Blood1', 'color': 'green', 'label_color': 'white'},
            2: {'name': 'Blood2', 'color': 'cyan', 'label_color': 'black'},
            3: {'name': 'Wall', 'color': 'blue', 'label_color': 'white'},
            4: {'name': 'Clot', 'color': 'orange', 'label_color': 'black'},
            5: {'name': 'Step', 'color': 'black', 'label_color': 'white'}
        }

        # Create menu bar
        self._create_menu_bar()

        # Create toolbar frame FIRST
        self.toolbar_frame = tk.Frame(self.root, bg='#B0C4DE', height=50)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Create plot area BEFORE initializing interaction modes
        self._create_plot_area()

        # Create interaction modes and toolbar
        from siglab_lib.mainWinSupport import InteractionModes, ToolbarUtils
        self.interaction_modes = InteractionModes(self)
        self.toolbar_utils = ToolbarUtils(self)
        
        # Create toolbar buttons USING THE NEW TOOLBAR FRAME
        self.toolbar_utils.create_toolbar_buttons(self.toolbar_frame)

        # Connect mouse events
        self.canvas.mpl_connect('button_press_event', self.interaction_modes.on_mouse_press)

    def _create_menu_bar(self):
        menubar = tk.Menu(self.root,background='#D0D8E0')
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self._open_file)
        file_menu.add_command(label="Save", command=self._save_file)
        file_menu.add_command(label="Save As", command=self._save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Calculate Menu
        calc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Calc", menu=calc_menu)
        calc_menu.add_command(label="Stats", command=self._calculate_stats)
        calc_menu.add_command(label="Higuchi", command=self._calculate_higuchi)
        calc_menu.add_command(label="All", command=self._calculate_all)

    def _create_toolbar(self):
        toolbar = tk.Frame(self.root, bg='#B0C4DE')
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Determine the width of the 'Unknown' button
        unknown_button_width = 10  # Adjust this value if needed

        # State selection buttons
        for state_val, state_info in self.state_colors.items():
            btn = tk.Button(
                toolbar, 
                text=state_info['name'], 
                bg=state_info['color'],
                fg=state_info['label_color'],
                width=unknown_button_width,  # Set consistent width
                command=lambda s=state_val: self._set_state_mode(s),
                anchor='center'  # Center the text horizontally
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)

    def _create_plot_area(self):
        # Create figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(15, 8)) 
        self.fig.patch.set_facecolor('#B0C4DE') 
        self.ax.set_facecolor('#E6EDF3') 
        self.ax.grid(True,linestyle='--',color='darkgray') 
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Connect mouse events 
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.canvas.mpl_connect('button_release_event', self._on_mouse_release) 
        


    def _open_file(self):
        # Open HDF5 file and load data
        filepath = tk.filedialog.askopenfilename(
            filetypes=[("F5B files", "*.f5b")]
        )
        if filepath:
            with h5py.File(filepath, 'r') as f:
                self.magR = f['signal/magR'][:]
                self.time_S = f['signal/time_S'][:]
                self.tag_state = f['tag/state'][:]
                self.filepath = filepath

            self._plot_data()

    def _plot_data(self):
        # Clear previous plot
        self.ax.clear()

        # Plot main signal FIRST (gray line in the background)
        self.ax.plot(self.time_S, self.magR, color='gray', zorder=1)

        # Plot state markers ON TOP of the signal line
        for state_val, state_info in self.state_colors.items():
            # Find indices for this state
            state_mask = self.tag_state == state_val
            state_time = self.time_S[::30][state_mask]
            state_mag = self.magR[::30][state_mask]

            # Plot state markers with higher zorder to ensure they're on top
            self.ax.scatter(state_time, state_mag, 
                            color=state_info['color'], 
                            label=state_info['name'],
                            zorder=2)  # Higher zorder to plot on top of the line

        # Set plot title using case file name
        self.ax.set_title(f'Signal: {os.path.basename(self.filepath)}')
        
        # Set x and y axis labels
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Magnitude (magR)')

        # Autoscale with minimal padding
        self.ax.set_xlim(self.time_S[0], self.time_S[-1])
        self.ax.set_ylim(
            self.magR.min() - abs(self.magR.min()) * 0.05,  # Small padding below min
            self.magR.max() + abs(self.magR.max()) * 0.05   # Small padding above max
        )

        # Re-apply grid settings
        self.ax.grid(True, linestyle='--', color='darkgray')

        # Adjust plot margins
        self.fig.tight_layout(pad=1.0)

        self.ax.legend()
        self.canvas.draw()

    def _set_state_mode(self, state_val):
        # State selection mode
        pass

    def _on_mouse_press(self, event):
        # Handle mouse press for state selection
        pass

    def _on_mouse_move(self, event):
        # Handle mouse move
        pass

    def _on_mouse_release(self, event):
        # Handle mouse release
        pass

    def _save_file(self):
        # Save current state to file
        pass

    def _save_as_file(self):
        # Save to a new file
        pass

    def _calculate_stats(self):
        # Calculate signal statistics
        pass

    def _calculate_higuchi(self):
        # Calculate Higuchi Fractal Dimension
        pass

    def _calculate_all(self):
        # Calculate all available metrics
        pass

def main():
    root = tk.Tk()
    app = SignalLab(root)
    root.mainloop()

if __name__ == "__main__":
    main()