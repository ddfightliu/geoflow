"""
Enhanced Well Section View Widget - Petrel-style implementation.

This module provides a professional well log visualization widget similar to
Petrel software, with multi-track display, interactive navigation, and
interpretation tools.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Rectangle
from matplotlib.widgets import SpanSelector
import matplotlib.gridspec as gridspec
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QAction
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd
import json
import os

from ..well_data import WellDataManager, WellLogData


class Track:
    """Represents a single track in the well section display."""

    def __init__(self, name: str, width: float = 1.0, color: str = 'black'):
        self.name = name
        self.width = width
        self.color = color
        self.curves: List[str] = []
        self.axis = None
        self.fill_between = None

    def add_curve(self, curve_name: str):
        """Add a curve to this track."""
        if curve_name not in self.curves:
            self.curves.append(curve_name)

    def remove_curve(self, curve_name: str):
        """Remove a curve from this track."""
        if curve_name in self.curves:
            self.curves.remove(curve_name)


class WellSectionCanvas(FigureCanvas):
    """Custom matplotlib canvas for well section display."""

    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.figure = plt.Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        self.parent = parent
        self.depth_range = (0, 1000)  # Default depth range
        self.tracks: List[Track] = []
        self.well_data = None
        self.depth_curve = None

        # Drag state variables
        self.dragging = False
        self.drag_track_idx = None
        self.drag_start_x = None

        # Connect mouse events
        self.mpl_connect('scroll_event', self.on_scroll)
        self.mpl_connect('button_press_event', self.on_click)
        self.mpl_connect('button_release_event', self.on_release)
        self.mpl_connect('motion_notify_event', self.on_motion)

        # Initialize display
        self.setup_display()

    def setup_display(self):
        """Set up the multi-track display layout."""
        self.figure.clear()

        if not self.tracks:
            # Default tracks
            self.tracks = [
                Track("Depth", 0.5, 'black'),
                Track("GR", 1.0, 'green'),
                Track("Resistivity", 1.0, 'blue'),
                Track("Density", 1.0, 'red'),
                Track("Neutron", 1.0, 'purple'),
            ]

        # Calculate total width
        total_width = sum(track.width for track in self.tracks)

        # Create subplots with custom widths
        gs = gridspec.GridSpec(1, len(self.tracks), wspace=0.1,
                              width_ratios=[t.width for t in self.tracks])

        for i, track in enumerate(self.tracks):
            track.axis = self.figure.add_subplot(gs[i])
            track.axis.set_title(track.name, fontsize=10, pad=5)
            track.axis.grid(True, alpha=0.3)

            # Configure axis
            if i == 0:  # Depth track
                track.axis.set_ylabel('Depth (ft)')
                track.axis.tick_params(axis='y', labelsize=8)
                track.axis.set_xlim(0, 1)
            else:
                track.axis.set_yticklabels([])
                track.axis.tick_params(axis='y', labelleft=False)

            track.axis.set_ylim(self.depth_range[1], self.depth_range[0])  # Inverted for depth

        self.draw()

    def set_well_data(self, well_data: WellLogData):
        """Set the well data for display."""
        self.well_data = well_data
        self.depth_curve = well_data._find_depth_curve()

        if self.depth_curve:
            depth_data = well_data.get_curve_data(self.depth_curve)
            if depth_data is not None:
                self.depth_range = (np.min(depth_data), np.max(depth_data))

        self.update_display()

    def update_display(self):
        """Update the display with current well data."""
        if not self.well_data:
            return

        # Clear all tracks
        for track in self.tracks:
            track.axis.clear()
            track.axis.set_title(track.name, fontsize=10, pad=5)
            track.axis.grid(True, alpha=0.3)
            track.axis.set_ylim(self.depth_range[1], self.depth_range[0])

        # Get depth data
        depth_data = self.well_data.get_curve_data(self.depth_curve) if self.depth_curve else None
        if depth_data is None:
            depth_data = np.arange(len(self.well_data.data))

        # Plot curves in appropriate tracks
        curve_colors = {
            'GR': 'green', 'GR_EDTC': 'green',
            'RHOB': 'red', 'RHOZ': 'red',
            'NPHI': 'blue', 'NPOR': 'blue',
            'RT': 'purple', 'ILD': 'purple', 'LLD': 'purple',
            'DT': 'orange', 'DTC': 'orange',
        }

        for curve_name in self.well_data.get_curve_names():
            curve_data = self.well_data.get_curve_data(curve_name)
            if curve_data is None:
                continue

            # Determine which track to use
            track_idx = self._get_track_for_curve(curve_name)
            if track_idx >= len(self.tracks):
                continue

            track = self.tracks[track_idx]
            color = curve_colors.get(curve_name, 'black')

            # Plot the curve
            track.axis.plot(curve_data, depth_data, color=color, linewidth=1.5, label=curve_name)

            # Set axis limits based on data
            if track_idx > 0:  # Not depth track
                data_min, data_max = np.nanmin(curve_data), np.nanmax(curve_data)
                if np.isfinite(data_min) and np.isfinite(data_max):
                    margin = (data_max - data_min) * 0.1
                    track.axis.set_xlim(data_min - margin, data_max + margin)

        # Configure depth track
        depth_track = self.tracks[0]
        depth_track.axis.set_xlim(0, 1)
        depth_track.axis.set_ylabel('Depth (ft)', fontsize=10)
        depth_track.axis.tick_params(axis='y', labelsize=8)

        # Hide y-labels for other tracks
        for track in self.tracks[1:]:
            track.axis.set_yticklabels([])
            track.axis.tick_params(axis='y', labelleft=False)

        # Add legends
        for track in self.tracks[1:]:
            if track.axis.get_lines():
                track.axis.legend(loc='upper right', fontsize=8)

        self.figure.suptitle(f"Well Section - {self.well_data.name if self.well_data else 'No Well Loaded'}",
                           fontsize=12, y=0.98)
        self.figure.tight_layout()
        self.draw()

    def _get_track_for_curve(self, curve_name: str) -> int:
        """Determine which track index a curve should be plotted in."""
        curve_track_map = {
            # Depth track (0)
            'DEPT': 0, 'DEPTH': 0, 'MD': 0, 'TVD': 0,

            # Gamma Ray track (1)
            'GR': 1, 'GR_EDTC': 1, 'CGR': 1,

            # Resistivity track (2)
            'RT': 2, 'ILD': 2, 'LLD': 2, 'MSFL': 2, 'LLS': 2,

            # Density track (3)
            'RHOB': 3, 'RHOZ': 3, 'DRHO': 3,

            # Neutron track (4)
            'NPHI': 4, 'NPOR': 4, 'TNPH': 4,
        }

        return curve_track_map.get(curve_name, 1)  # Default to GR track

    def _get_track_at_position(self, x_pixel: float, x_data: float) -> Optional[int]:
        """Determine which track is at the given pixel position for resizing."""
        if not self.tracks:
            return None

        # Get the figure dimensions
        fig_width = self.figure.get_size_inches()[0] * self.figure.dpi

        # Calculate cumulative widths
        total_width = sum(track.width for track in self.tracks)
        cumulative_width = 0

        for i, track in enumerate(self.tracks):
            track_width_pixels = (track.width / total_width) * fig_width
            if cumulative_width <= x_pixel < cumulative_width + track_width_pixels:
                # Check if near the right boundary (within 5 pixels)
                if x_pixel >= cumulative_width + track_width_pixels - 5:
                    return i
                break
            cumulative_width += track_width_pixels

        return None

    def zoom_to_depth_range(self, min_depth: float, max_depth: float):
        """Zoom to a specific depth range."""
        self.depth_range = (min_depth, max_depth)
        for track in self.tracks:
            track.axis.set_ylim(max_depth, min_depth)
        self.draw()

    def fit_to_data(self):
        """Fit the view to show all data."""
        if self.well_data and self.depth_curve:
            depth_data = self.well_data.get_curve_data(self.depth_curve)
            if depth_data is not None:
                self.depth_range = (np.min(depth_data), np.max(depth_data))
                self.zoom_to_depth_range(*self.depth_range)

    def on_scroll(self, event):
        """Handle mouse wheel zoom."""
        if event.button == 'up':
            # Zoom in
            depth_span = self.depth_range[1] - self.depth_range[0]
            center = (self.depth_range[0] + self.depth_range[1]) / 2
            new_span = depth_span * 0.9
            self.zoom_to_depth_range(center - new_span/2, center + new_span/2)
        elif event.button == 'down':
            # Zoom out
            depth_span = self.depth_range[1] - self.depth_range[0]
            center = (self.depth_range[0] + self.depth_range[1]) / 2
            new_span = depth_span * 1.1
            self.zoom_to_depth_range(center - new_span/2, center + new_span/2)

    def on_click(self, event):
        """Handle mouse click events."""
        if event.button == 1 and event.inaxes:  # Left click
            # Check if clicking near track boundary for resizing
            track_idx = self._get_track_at_position(event.x, event.xdata)
            if track_idx is not None and track_idx > 0:  # Not the depth track
                self.dragging = True
                self.drag_track_idx = track_idx
                self.drag_start_x = event.xdata
                return

            # Find depth at click position
            depth = event.ydata
            if self.parent:
                self.parent.update_depth_cursor(depth)

    def on_release(self, event):
        """Handle mouse button release events."""
        if self.dragging and self.drag_track_idx is not None:
            self.dragging = False
            self.drag_track_idx = None
            self.drag_start_x = None
            self.draw()

    def on_motion(self, event):
        """Handle mouse motion for cursor tracking."""
        if self.dragging and self.drag_track_idx is not None and event.xdata is not None:
            # Handle track resizing during drag
            current_x = event.xdata
            delta_x = current_x - self.drag_start_x

            # Convert pixel delta to width adjustment (simplified)
            # This is a basic implementation - you might want to refine the scaling
            width_change = delta_x * 0.01  # Adjust sensitivity as needed

            if self.drag_track_idx < len(self.tracks):
                track = self.tracks[self.drag_track_idx]
                new_width = max(0.1, track.width + width_change)  # Minimum width
                track.width = new_width

                # Refresh display with new widths
                self.setup_display()
                if self.well_data:
                    self.set_well_data(self.well_data)

        elif event.inaxes and self.parent:
            depth = event.ydata
            self.parent.update_depth_info(depth)


class EnhancedWellSectionWidget(QtWidgets.QWidget):
    """Enhanced Well Section View Widget with Petrel-like functionality."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.well_manager = WellDataManager()
        self.current_well = None
        self.canvas = None
        self.toolbar = None
        self.depth_cursor = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the enhanced well section UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Top toolbar
        self.create_toolbar()
        layout.addWidget(self.toolbar)

        # Control panel
        control_layout = QtWidgets.QHBoxLayout()

        # Well selector
        well_layout = QtWidgets.QVBoxLayout()
        well_layout.addWidget(QtWidgets.QLabel("Well:"))
        self.well_combo = QtWidgets.QComboBox()
        self.well_combo.addItem("Select Well...")
        self.well_combo.currentTextChanged.connect(self.on_well_selected)
        well_layout.addWidget(self.well_combo)
        control_layout.addLayout(well_layout)

        # Load well button
        self.load_well_btn = QtWidgets.QPushButton("Load Well")
        self.load_well_btn.clicked.connect(self.load_well)
        control_layout.addWidget(self.load_well_btn)

        # Depth range controls
        depth_layout = QtWidgets.QVBoxLayout()
        depth_layout.addWidget(QtWidgets.QLabel("Depth Range:"))

        depth_input_layout = QtWidgets.QHBoxLayout()
        self.min_depth_edit = QtWidgets.QLineEdit("0")
        self.min_depth_edit.setFixedWidth(80)
        self.min_depth_edit.returnPressed.connect(self.update_depth_range)
        depth_input_layout.addWidget(QtWidgets.QLabel("Min:"))
        depth_input_layout.addWidget(self.min_depth_edit)

        self.max_depth_edit = QtWidgets.QLineEdit("1000")
        self.max_depth_edit.setFixedWidth(80)
        self.max_depth_edit.returnPressed.connect(self.update_depth_range)
        depth_input_layout.addWidget(QtWidgets.QLabel("Max:"))
        depth_input_layout.addWidget(self.max_depth_edit)

        depth_layout.addLayout(depth_input_layout)
        control_layout.addLayout(depth_layout)

        # Interpretation buttons
        interp_layout = QtWidgets.QVBoxLayout()
        interp_layout.addWidget(QtWidgets.QLabel("Interpretation:"))

        interp_btn_layout = QtWidgets.QHBoxLayout()
        self.calc_shale_btn = QtWidgets.QPushButton("Shale Volume")
        self.calc_shale_btn.clicked.connect(self.calculate_shale_volume)
        self.calc_shale_btn.setEnabled(False)
        interp_btn_layout.addWidget(self.calc_shale_btn)

        self.calc_porosity_btn = QtWidgets.QPushButton("Porosity")
        self.calc_porosity_btn.clicked.connect(self.calculate_porosity)
        self.calc_porosity_btn.setEnabled(False)
        interp_btn_layout.addWidget(self.calc_porosity_btn)

        interp_layout.addLayout(interp_btn_layout)
        control_layout.addLayout(interp_layout)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Canvas area
        self.canvas = WellSectionCanvas(self, width=12, height=8)
        layout.addWidget(self.canvas)

        # Status bar
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label)

        # Depth info label
        self.depth_info_label = QtWidgets.QLabel("Depth: -- | Value: --")
        layout.addWidget(self.depth_info_label)

    def create_toolbar(self):
        """Create the toolbar with navigation tools."""
        self.toolbar = QtWidgets.QToolBar("Well Section Tools")

        # Zoom to fit
        fit_action = QAction("Fit to Data", self)
        fit_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        fit_action.triggered.connect(self.fit_to_data)
        self.toolbar.addAction(fit_action)

        # Zoom in/out
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowUp))
        zoom_in_action.triggered.connect(self.zoom_in)
        self.toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowDown))
        zoom_out_action.triggered.connect(self.zoom_out)
        self.toolbar.addAction(zoom_out_action)

        self.toolbar.addSeparator()

        # Template actions
        save_template_action = QAction("Save Template", self)
        save_template_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DriveFDIcon))
        save_template_action.triggered.connect(self.save_template)
        self.toolbar.addAction(save_template_action)

        load_template_action = QAction("Load Template", self)
        load_template_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DriveFDIcon))
        load_template_action.triggered.connect(self.load_template)
        self.toolbar.addAction(load_template_action)

        self.toolbar.addSeparator()

        # Track configuration
        config_action = QAction("Configure Tracks", self)
        config_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_CustomBase))
        config_action.triggered.connect(self.configure_tracks)
        self.toolbar.addAction(config_action)

    def load_well(self):
        """Load a well from file."""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open LAS File", "", "LAS files (*.las)")
        if file_path:
            well_name = self.well_manager.load_well(file_path)
            if well_name:
                self.well_combo.addItem(well_name)
                self.well_combo.setCurrentText(well_name)
                self.status_label.setText(f"Loaded well: {well_name}")
            else:
                self.status_label.setText("Failed to load well")

    def on_well_selected(self, well_name):
        """Handle well selection change."""
        if well_name and well_name != "Select Well...":
            self.current_well = self.well_manager.get_well(well_name)
            if self.current_well:
                self.canvas.set_well_data(self.current_well)
                self.calc_shale_btn.setEnabled(True)
                self.calc_porosity_btn.setEnabled(True)
                self.status_label.setText(f"Selected well: {well_name}")

                # Update depth range inputs
                if self.canvas.depth_curve:
                    depth_data = self.current_well.get_curve_data(self.canvas.depth_curve)
                    if depth_data is not None:
                        self.min_depth_edit.setText(f"{np.min(depth_data):.0f}")
                        self.max_depth_edit.setText(f"{np.max(depth_data):.0f}")
            else:
                self.status_label.setText("Well not found")
        else:
            self.current_well = None
            self.calc_shale_btn.setEnabled(False)
            self.calc_porosity_btn.setEnabled(False)

    def update_depth_range(self):
        """Update the depth range from input fields."""
        try:
            min_depth = float(self.min_depth_edit.text())
            max_depth = float(self.max_depth_edit.text())
            if min_depth < max_depth:
                self.canvas.zoom_to_depth_range(min_depth, max_depth)
                self.status_label.setText(f"Depth range: {min_depth:.0f} - {max_depth:.0f} ft")
            else:
                self.status_label.setText("Invalid depth range")
        except ValueError:
            self.status_label.setText("Invalid depth values")

    def fit_to_data(self):
        """Fit the view to show all well data."""
        if self.canvas:
            self.canvas.fit_to_data()
            min_d, max_d = self.canvas.depth_range
            self.min_depth_edit.setText(f"{min_d:.0f}")
            self.max_depth_edit.setText(f"{max_d:.0f}")
            self.status_label.setText("Fitted to data")

    def zoom_in(self):
        """Zoom in on the current depth range."""
        if self.canvas:
            depth_span = self.canvas.depth_range[1] - self.canvas.depth_range[0]
            center = (self.canvas.depth_range[0] + self.canvas.depth_range[1]) / 2
            new_span = depth_span * 0.7
            self.canvas.zoom_to_depth_range(center - new_span/2, center + new_span/2)
            self.update_depth_inputs()

    def zoom_out(self):
        """Zoom out from the current depth range."""
        if self.canvas:
            depth_span = self.canvas.depth_range[1] - self.canvas.depth_range[0]
            center = (self.canvas.depth_range[0] + self.canvas.depth_range[1]) / 2
            new_span = depth_span * 1.4
            self.canvas.zoom_to_depth_range(center - new_span/2, center + new_span/2)
            self.update_depth_inputs()

    def update_depth_inputs(self):
        """Update the depth input fields to match current range."""
        min_d, max_d = self.canvas.depth_range
        self.min_depth_edit.setText(f"{min_d:.0f}")
        self.max_depth_edit.setText(f"{max_d:.0f}")

    def configure_tracks(self):
        """Open track configuration dialog."""
        # Placeholder for track configuration
        QtWidgets.QMessageBox.information(self, "Track Configuration",
                                        "Track configuration dialog would open here")

    def calculate_shale_volume(self):
        """Calculate and display shale volume."""
        if not self.current_well:
            return

        vsh = self.current_well.calculate_shale_volume()
        if vsh is None:
            self.status_label.setText("GR curve not found for shale volume calculation")
            return

        # Add shale volume as a new curve
        self.current_well.curves['VSH'] = vsh
        self.current_well.units['VSH'] = 'fraction'
        self.current_well.descriptions['VSH'] = 'Shale Volume'

        # Refresh display
        self.canvas.update_display()
        self.status_label.setText("Shale volume calculated")

    def calculate_porosity(self):
        """Calculate and display porosity."""
        if not self.current_well:
            return

        phi = self.current_well.calculate_porosity()
        if phi is None:
            self.status_label.setText("RHOB curve not found for porosity calculation")
            return

        # Add porosity as a new curve
        self.current_well.curves['PHI'] = phi
        self.current_well.units['PHI'] = 'fraction'
        self.current_well.descriptions['PHI'] = 'Porosity'

        # Refresh display
        self.canvas.update_display()
        self.status_label.setText("Porosity calculated")

    def update_depth_cursor(self, depth: float):
        """Update the depth cursor position."""
        self.depth_cursor = depth
        self.update_depth_info(depth)

    def update_depth_info(self, depth: float):
        """Update the depth information display."""
        if depth is not None:
            info_text = f"Depth: {depth:.1f} ft"
            if self.current_well and self.canvas.depth_curve:
                # Find closest depth index
                depth_data = self.current_well.get_curve_data(self.canvas.depth_curve)
                if depth_data is not None:
                    idx = np.argmin(np.abs(depth_data - depth))
                    info_text += f" | Index: {idx}"

                    # Add curve values at this depth
                    curve_values = []
                    for curve_name in ['GR', 'RHOB', 'NPHI', 'RT']:
                        if curve_name in self.current_well.curves:
                            value = self.current_well.curves[curve_name][idx]
                            if np.isfinite(value):
                                curve_values.append(f"{curve_name}: {value:.3f}")

                    if curve_values:
                        info_text += f" | {', '.join(curve_values[:3])}"  # Show first 3 curves

            self.depth_info_label.setText(info_text)
        else:
            self.depth_info_label.setText("Depth: -- | Value: --")

    def save_template(self):
        """Save current track configuration as a template."""
        if not self.canvas.tracks:
            QtWidgets.QMessageBox.warning(self, "No Tracks", "No tracks to save.")
            return

        # Get template name from user
        template_name, ok = QtWidgets.QInputDialog.getText(self, "Save Template",
                                                         "Enter template name:")
        if not ok or not template_name.strip():
            return

        # Serialize track configuration
        template_data = {
            'name': template_name.strip(),
            'tracks': []
        }

        for track in self.canvas.tracks:
            track_data = {
                'name': track.name,
                'width': track.width,
                'color': track.color,
                'curves': track.curves.copy()
            }
            template_data['tracks'].append(track_data)

        # Save to templates directory
        template_dir = Path('templates')
        template_dir.mkdir(exist_ok=True)
        template_file = template_dir / f"{template_name.strip().replace(' ', '_')}.json"

        try:
            with open(template_file, 'w') as f:
                json.dump(template_data, f, indent=2)
            self.status_label.setText(f"Template '{template_name}' saved")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save template: {str(e)}")

    def load_template(self):
        """Load track configuration from a template."""
        template_dir = Path('templates')
        if not template_dir.exists():
            QtWidgets.QMessageBox.information(self, "No Templates", "No templates directory found.")
            return

        # Get list of template files
        template_files = list(template_dir.glob('*.json'))
        if not template_files:
            QtWidgets.QMessageBox.information(self, "No Templates", "No template files found.")
            return

        # Create file dialog for template selection
        file_dialog = QtWidgets.QFileDialog(self, "Load Template", str(template_dir), "JSON files (*.json)")
        file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                template_file = Path(selected_files[0])

                try:
                    with open(template_file, 'r') as f:
                        template_data = json.load(f)

                    # Apply template configuration
                    self.canvas.tracks = []
                    for track_data in template_data['tracks']:
                        track = Track(
                            name=track_data['name'],
                            width=track_data['width'],
                            color=track_data['color']
                        )
                        track.curves = track_data['curves']
                        self.canvas.tracks.append(track)

                    # Refresh display
                    self.canvas.setup_display()
                    if self.current_well:
                        self.canvas.set_well_data(self.current_well)

                    self.status_label.setText(f"Template '{template_data['name']}' loaded")

                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Load Error", f"Failed to load template: {str(e)}")


# Update the main views.py to use the enhanced widget
def create_well_section_view(parent=None):
    """Factory function to create the enhanced well section view."""
    return EnhancedWellSectionWidget(parent)
