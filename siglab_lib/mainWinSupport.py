# siglab_lib/mainWinSupport.py
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

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
        
        # Setup rectangular selector for zoom
        self.rect_selector = RectangleSelector(
            self.app.ax, 
            self._zoom_select_callback,
            useblit=True,
            button=[1],  # Left mouse button
            minspanx=5, 
            minspany=5,
            spancoords='pixels'
        )
        self.rect_selector.set_active(False)



    def _zoom_select_callback(self, eclick, erelease):
        """Callback for rectangle zoom"""
        x1, x2 = eclick.xdata, erelease.xdata
        y1, y2 = eclick.ydata, erelease.ydata
        
        # Set new plot limits
        self.app.ax.set_xlim(min(x1, x2), max(x1, x2))
        self.app.ax.set_ylim(min(y1, y2), max(y1, y2))
        self.app.canvas.draw()

    def reset_view(self):
        """Reset plot to original view"""
        if self.app.time_S is not None:
            self.app.ax.set_xlim(self.app.time_S[0], self.app.time_S[-1])
            self.app.ax.set_ylim(
                self.app.magR.min() - abs(self.app.magR.min()) * 0.05,
                self.app.magR.max() + abs(self.app.magR.max()) * 0.05
            )
            self.app.canvas.draw()

    def set_state_mode(self, state_val):
        # Remove any existing mode text
        if hasattr(self, 'mode_text'):
            self.mode_text.remove()
            del self.mode_text
            self.app.canvas.draw()

        if self.interaction_mode == 'state_select' and self.current_state_selection == state_val:
            # Deactivate if same state is selected again
            self.interaction_mode = None
            self.current_state_selection = None
            self.selection_points = []
        else:
            # Activate state selection mode
            self.interaction_mode = 'state_select'
            self.current_state_selection = state_val
            self.selection_points = []
            
            # Deactivate zoom
            self.rect_selector.set_active(False)
            
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

    def toggle_zoom_mode(self):
        # Remove any existing mode text
        if hasattr(self, 'mode_text'):
            self.mode_text.remove()
            del self.mode_text
            self.app.canvas.draw()

        if self.interaction_mode == 'zoom':
            # Deactivate zoom
            self.interaction_mode = None
            self.rect_selector.set_active(False)
        else:
            # Activate zoom
            self.interaction_mode = 'zoom'
            self.rect_selector.set_active(True)
            
            # Add text to figure with red background
            self.mode_text = self.app.fig.text(
                0.5, 0.95, 
                "Zoom Mode", 
                transform=self.app.fig.transFigure,
                horizontalalignment='center',
                verticalalignment='top',
                bbox=dict(facecolor='red', alpha=0.7, edgecolor='darkred')
            )
            self.app.canvas.draw()
            
            # Reset other modes
            self.current_state_selection = None
            self.selection_points = []

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
            
            # Replot to show updated states
            self.app._plot_data()  # Remove reset_view argument
            
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

    def create_toolbar_buttons(self, toolbar):
        """
        Create buttons for different interactions
        
        Parameters:
        - toolbar: The toolbar frame to add buttons to
        """
        unknown_button_width = 10

        # Zoom button
        zoom_btn = tk.Button(
            toolbar, 
            text='Zoom', 
            width=unknown_button_width,
            command=self.app.interaction_modes.toggle_zoom_mode,
            anchor='center'
        )
        zoom_btn.pack(side=tk.LEFT, padx=5, pady=5)

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