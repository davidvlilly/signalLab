# siglab_lib/mainWinSupport.py
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

class InteractionModes:
    def __init__(self, app):
        """
        Initialize interaction modes for the SignalLab application
        
        Parameters:
        - app: Main application instance
        """
        self.app = app
        self.interaction_mode = None
        self.current_state_selection = None
        self.selection_points = []


    def reset_view(self):
        """Reset zoom mode and toolbar"""
        # Reset interaction mode
        self.interaction_mode = None
        self.rect_selector.set_active(False)
        
        try:
            # Attempt to reset toolbar mode programmatically
            if hasattr(self.app.toolbar, 'mode'):
                # Try to set mode to a non-zoom state
                self.app.toolbar.mode = None  # or try other potential reset values
            
            # Additional reset attempts
            if hasattr(self.app.toolbar, '_zoom_mode'):
                self.app.toolbar._zoom_mode = False
            
            # Call home method to reset view
            self.app.toolbar.home()
        except Exception as e:
            print(f"Error resetting toolbar mode: {e}")
        
        # Disable all buttons in the toolbar
        try:
            for child in self.app.toolbar.winfo_children():
                if isinstance(child, (tk.Button, tk.Checkbutton)):
                    child.configure(state='disabled')
        except Exception as e:
            print(f"Error disabling toolbar buttons: {e}")
        
        # Force redraw
        self.app.canvas.draw()

    def deactivate_plot_menubar(self):
        """Deactivate plot menubar buttons and zoom/pan modes"""
        try:
            # Reset toolbar mode
            if hasattr(self.app.toolbar, 'mode'):
                self.app.toolbar.mode = None
            
            # Disable all buttons in the toolbar
            for child in self.app.toolbar.winfo_children():
                if isinstance(child, (tk.Button, tk.Checkbutton)):
                    child.configure(state='disabled')
            
            # Deactivate rectangle selector
            self.rect_selector.set_active(False)
        except Exception as e:
            print(f"Error deactivating plot menubar: {e}")

    def restore_plot_menubar(self):
        """Restore access to plot menubar buttons"""
        try:
            # Re-enable all buttons in the toolbar
            for child in self.app.toolbar.winfo_children():
                if isinstance(child, (tk.Button, tk.Checkbutton)):
                    child.configure(state='normal')
        except Exception as e:
            print(f"Error restoring plot menubar: {e}")

    def set_state_mode(self, state_val):
        # Remove any existing mode text
        if hasattr(self, 'mode_text'):
            self.mode_text.remove()
            del self.mode_text
            self.app.canvas.draw()

        # If already in a different mode, cancel that mode first
        if self.interaction_mode is not None and self.interaction_mode != 'state_select':
            # Restore plot menubar for previous mode
            self.restore_plot_menubar()

        if self.interaction_mode == 'state_select' and self.current_state_selection == state_val:
            # Deactivate if same state is selected again
            self.interaction_mode = None
            self.current_state_selection = None
            self.selection_points = []
            
            # Restore plot menubar
            self.restore_plot_menubar()
        else:
            # Activate state selection mode
            self.interaction_mode = 'state_select'
            self.current_state_selection = state_val
            self.selection_points = []
            
            # Deactivate plot menubar
            self.deactivate_plot_menubar()
            
            # Add text to figure with red background
            state_name = self.app.state_colors[state_val]['name']
            self.mode_text = self.app.fig.text(
                0.5, 0.95, 
                f"{state_name} Mode", 
                transform=self.app.fig.transFigure,
                horizontalalignment='center',
                verticalalignment='top',
                bbox=dict(facecolor='red', alpha=0.7, edgecolor='darkred')
            )
            self.app.canvas.draw()



    def on_mouse_press(self, event):
        """Handle mouse press for state selection"""
        if self.interaction_mode == 'state_select' and event.inaxes == self.app.ax:
            self.selection_points.append(event.xdata)
            
            # Visualize selection points
            color = 'red' if len(self.selection_points) == 1 else 'blue'
            self.app.ax.axvline(x=event.xdata, color=color, linestyle='--', alpha=0.5)
            self.app.canvas.draw()
            
            # Complete state selection if two points are selected
            if len(self.selection_points) == 2:
                self._complete_state_selection()

    def _complete_state_selection(self):
        """Apply selected state to specified time range"""
        if len(self.selection_points) == 2:
            # Ensure points are in correct order
            xmin, xmax = sorted(self.selection_points)
            
            # Find indices in tag_state that fall within this range
            mask = (self.app.time_S[::30] >= xmin) & (self.app.time_S[::30] <= xmax)
            self.app.tag_state[mask] = self.current_state_selection
            
            # Replot to show updated states WITHOUT rescaling
            self.app._plot_data(rescale=False)
            
            # Reset selection
            self.selection_points = []
            
          

class ToolbarUtils:
    def __init__(self, app):
        """
        Initialize toolbar utilities for the SignalLab application
        
        Parameters:
        - app: Main application instance
        """
        self.app = app

class ToolbarUtils:
    def __init__(self, app):
        """
        Initialize toolbar utilities for the SignalLab application
        
        Parameters:
        - app: Main application instance
        """
        self.app = app

    def create_toolbar_buttons(self, toolbar):
        """
        Create buttons for different interactions
        
        Parameters:
        - toolbar: The toolbar frame to add buttons to
        """
        unknown_button_width = 10

        # Reset view button
        reset_btn = tk.Button(
            toolbar, 
            text='Reset View', 
            width=unknown_button_width,
            command=self.app.interaction_modes.reset_view,
            anchor='center'
        )
        reset_btn.pack(side=tk.LEFT, padx=5, pady=5)

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