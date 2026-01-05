import os
import sys
import tkinter as tk
from tkinter import messagebox
import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from siglab_lib.mainWinSupport import InteractionModes, ToolbarUtils
from siglab_lib.fileIO import FileOperations
from siglab_lib.mainWinPlot import MainWindowPlotter
from siglab_lib.calcStats import calculate_segment_stats
from siglab_lib.externalPlot import create_stats_plot, create_higuchi_plot

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
        self.stats = None

        # State colors
        self.state_colors = {
            0: {'name': 'Unknown', 'color': 'gray', 'label_color': 'white'},
            1: {'name': 'Blood1', 'color': 'green', 'label_color': 'white'},
            2: {'name': 'Blood2', 'color': 'cyan', 'label_color': 'black'},
            3: {'name': 'Wall', 'color': 'blue', 'label_color': 'white'},
            4: {'name': 'Clot', 'color': 'orange', 'label_color': 'black'},
            5: {'name': 'Step', 'color': 'black', 'label_color': 'white'}
        }

        # Create toolbar/plot_utils/canvas
        self.file_ops = FileOperations(self)
        self._create_menu_bar()
        self.toolbar_frame = tk.Frame(self.root, bg='#B0C4DE', height=50)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.plot_utils = MainWindowPlotter(self)
        self.plot_utils.create_plot_area()
        self.interaction_modes = InteractionModes(self)
        self.toolbar_utils = ToolbarUtils(self)
        self.toolbar_utils.create_toolbar_buttons(self.toolbar_frame)
        self.canvas.mpl_connect('button_press_event', self.interaction_modes.on_mouse_press)
        

    def _create_menu_bar(self):
        menubar = tk.Menu(self.root, background='#D0D8E0')
        self.root.config(menu=menubar)

        # File Menu (existing code remains the same)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.file_ops.open_file)
        file_menu.add_command(label="Save", command=self.file_ops.save_file)
        file_menu.add_command(label="Save As", command=self.file_ops.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Calculate Menu (existing code remains the same)
        calc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Calc", menu=calc_menu)
        calc_menu.add_command(label="Stats", command=self._calculate_stats)
        calc_menu.add_command(label="Higuchi", command=self._calculate_higuchi)
        calc_menu.add_command(label="All", command=self._calculate_all)

        # Time-Plot Menu (renamed from Plot)
        time_plot_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Time-Plot", menu=time_plot_menu)
        time_plot_menu.add_command(label="Stats", command=self._plot_stats)
        time_plot_menu.add_command(label="Higuchi", command=self._plot_higuchi)

        # NEW: Scatter-Plot Menu
        scatter_plot_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Scatter-Plot", menu=scatter_plot_menu)
        scatter_plot_menu.add_command(label="Higuchi", command=self._scatter_plot_higuchi)
        scatter_plot_menu.add_command(label="Range Vs BloodRefDiff", command=self._scatter_plot_range_bloodref)


    def create_toolbar_buttons(self, toolbar):
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
            
    def _calculate_stats(self):
        """Calculate and store signal statistics"""
        from siglab_lib.calcStats import calculate_segment_stats       
        # Calculate comprehensive statistics
        self.stats = calculate_segment_stats(self)      
        #print("bloodEstVal:", *[int(val) for val in self.stats['bloodEstVal'][:30]])
        #print("bloodEstRng:", *[int(val) for val in self.stats['bloodEstRng'][:30]])
        
    def _plot_stats(self):
        """Launch external stats plot"""
        if self.stats is None:
            tk.messagebox.showinfo("Stats Plot", "Please calculate stats first using Calc > Stats")
            return
        
        from siglab_lib.externalPlot import create_stats_plot
        create_stats_plot(self)

    def _calculate_higuchi(self):
        """Calculate and store Higuchi Fractal Dimension statistics"""
        from siglab_lib.calcHiguchi import calculate_higuchi_stats
        
        # Calculate Higuchi statistics
        self.higuchi_stats = calculate_higuchi_stats(self.magR, self.time_S)
        
        # Optional: Print some stats
        print("Higuchi Fractal Dimension statistics calculated")

    def _plot_higuchi(self):
        """Launch external Higuchi plot"""
        if not hasattr(self, 'higuchi_stats') or self.higuchi_stats is None:
            tk.messagebox.showinfo("Higuchi Plot", "Please calculate Higuchi stats first using Calc > Higuchi")
            return
        
        from siglab_lib.externalPlot import create_higuchi_plot
        create_higuchi_plot(self)
        
    def _scatter_plot_higuchi(self):
        """Launch Higuchi scatter plot"""
        from siglab_lib.scatterPlot import create_higuchi_scatter
        create_higuchi_scatter(self)

    def _scatter_plot_range_bloodref(self):
        """Launch Range vs Blood Reference Difference scatter plot"""
        from siglab_lib.scatterPlot import create_range_bloodref_scatter
        create_range_bloodref_scatter(self)



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


    def _calculate_all(self):
        # Calculate all available metrics
        pass

def main():
    root = tk.Tk()
    app = SignalLab(root)
    root.mainloop()

if __name__ == "__main__":
    main()