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
from siglab_lib.fileIO import FileOperations
from siglab_lib.mainWinPlot import MainWindowPlotter

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

        # State colors
        self.state_colors = {
            0: {'name': 'Unknown', 'color': 'gray', 'label_color': 'white'},
            1: {'name': 'Blood1', 'color': 'green', 'label_color': 'white'},
            2: {'name': 'Blood2', 'color': 'cyan', 'label_color': 'black'},
            3: {'name': 'Wall', 'color': 'blue', 'label_color': 'white'},
            4: {'name': 'Clot', 'color': 'orange', 'label_color': 'black'},
            5: {'name': 'Step', 'color': 'black', 'label_color': 'white'}
        }

        # Create file operations
        self.file_ops = FileOperations(self)

        # Create menu bar
        self._create_menu_bar()

        # Create toolbar frame
        self.toolbar_frame = tk.Frame(self.root, bg='#B0C4DE', height=50)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Create plot plotter
        self.plot_utils = MainWindowPlotter(self)

        # Create plot area
        self.plot_utils.create_plot_area()

        # Create interaction modes and toolbar
        self.interaction_modes = InteractionModes(self)
        self.toolbar_utils = ToolbarUtils(self)
        
        # Create toolbar buttons
        self.toolbar_utils.create_toolbar_buttons(self.toolbar_frame)

        # Connect mouse events
        self.canvas.mpl_connect('button_press_event', self.interaction_modes.on_mouse_press)
        

    def _create_menu_bar(self):
        menubar = tk.Menu(self.root,background='#D0D8E0')
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.file_ops.open_file)
        file_menu.add_command(label="Save", command=self.file_ops.save_file)
        file_menu.add_command(label="Save As", command=self.file_ops.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Calculate Menu
        calc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Calc", menu=calc_menu)
        calc_menu.add_command(label="Stats", command=self._calculate_stats)
        calc_menu.add_command(label="Higuchi", command=self._calculate_higuchi)
        calc_menu.add_command(label="All", command=self._calculate_all)

    def create_toolbar_buttons(self, toolbar):
        """
        Create buttons for different interactions
        
        Parameters:
        - toolbar: The toolbar frame to add buttons to
        """
        unknown_button_width = 10

        # Escape button
        escape_btn = tk.Button(
            toolbar, 
            text='Escape', 
            width=unknown_button_width,
            command=self.app.interaction_modes.escape_interactive_mode,
            anchor='center'
        )
        escape_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # State selection buttons
        for state_val, state_info in self.app.state_colors.items():
            btn = tk.Button(
                toolbar, 
                text=state_info['name'], 
                bg=state_info['color'],
                fg=state_info['label_color'],
                width=unknown_button_width,
                command=lambda s=state_val: self.app.interaction_modes.set_state_mode(s),
                anchor='center'
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)



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