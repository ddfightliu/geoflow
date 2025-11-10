"""
View windows for geoflow application.

This module contains classes for different view types like 3D, Map, and Well Section views,
similar to Petrel software.
"""

from enum import Enum
from typing import Optional

from PySide6 import QtWidgets, QtCore
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from ..well_data import WellDataManager, WellLogData
from .well_section import create_well_section_view
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class ViewType(Enum):
    """Enumeration of available view types."""
    VIEW_3D = "3D"
    VIEW_MAP = "Map"
    VIEW_WELL_SECTION = "Well Section"


class BaseViewWidget(QtWidgets.QWidget):
    """Base class for all view widgets."""

    def __init__(self, view_type: ViewType, parent=None):
        super().__init__(parent)
        self.view_type = view_type
        self.setWindowTitle(f"{view_type.value} View")

    def get_view_data(self) -> dict:
        """Get view configuration data for saving."""
        return {
            'type': self.view_type.value,
            'title': self.windowTitle(),
        }


class View3DWidget(BaseViewWidget):
    """3D visualization view using PyVista."""

    def __init__(self, parent=None):
        super().__init__(ViewType.VIEW_3D, parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the 3D view UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Create PyVista plotter widget
        self.plotter = BackgroundPlotter(show=False)
        self.plotter.set_background('black')

        # Add the plotter widget to layout
        layout.addWidget(self.plotter.interactor)

        # Add some sample data for demonstration
        self.add_sample_data()

    def add_sample_data(self):
        """Add sample 3D data to the plotter."""
        # Create a simple sphere
        sphere = pv.Sphere(radius=0.5, center=(0, 0, 0))
        self.plotter.add_mesh(sphere, color='lightblue', opacity=0.8)

        # Create a cube
        cube = pv.Cube(center=(1, 1, 1))
        self.plotter.add_mesh(cube, color='orange', opacity=0.6)

        # Add axes
        self.plotter.add_axes()

        # Reset camera
        self.plotter.reset_camera()


class ViewMapWidget(BaseViewWidget):
    """Map view widget for geographic data."""

    def __init__(self, parent=None):
        super().__init__(ViewType.VIEW_MAP, parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the map view UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Placeholder for map widget
        self.map_label = QtWidgets.QLabel("Map View - Geographic Visualization")
        self.map_label.setAlignment(QtCore.Qt.AlignCenter)
        self.map_label.setStyleSheet("background-color: lightgreen; border: 1px solid black;")
        layout.addWidget(self.map_label)

        # Add some sample map elements
        self.add_sample_map_data()

    def add_sample_map_data(self):
        """Add sample map data."""
        # This would integrate with a mapping library like folium or pydeck
        # For now, just show placeholder text
        info_label = QtWidgets.QLabel("Sample wells and seismic lines would be displayed here")
        self.layout().addWidget(info_label)


class ViewWellSectionWidget(BaseViewWidget):
    """Well section view widget with interpretation tools."""

    def __init__(self, parent=None):
        super().__init__(ViewType.VIEW_WELL_SECTION, parent)
        # Use the enhanced well section widget
        self.enhanced_widget = create_well_section_view(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.enhanced_widget)
        layout.setContentsMargins(0, 0, 0, 0)

    def setup_ui(self):
        """Set up the well section view UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Top control panel
        control_layout = QtWidgets.QHBoxLayout()

        # Well selector
        self.well_combo = QtWidgets.QComboBox()
        self.well_combo.addItem("Select Well...")
        self.well_combo.currentTextChanged.connect(self.on_well_selected)
        control_layout.addWidget(QtWidgets.QLabel("Well:"))
        control_layout.addWidget(self.well_combo)

        # Load well button
        self.load_well_btn = QtWidgets.QPushButton("Load Well")
        self.load_well_btn.clicked.connect(self.load_well)
        control_layout.addWidget(self.load_well_btn)

        # Interpretation buttons
        self.calc_shale_btn = QtWidgets.QPushButton("Calculate Shale Volume")
        self.calc_shale_btn.clicked.connect(self.calculate_shale_volume)
        self.calc_shale_btn.setEnabled(False)
        control_layout.addWidget(self.calc_shale_btn)

        self.calc_porosity_btn = QtWidgets.QPushButton("Calculate Porosity")
        self.calc_porosity_btn.clicked.connect(self.calculate_porosity)
        self.calc_porosity_btn.setEnabled(False)
        control_layout.addWidget(self.calc_porosity_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Curve selection
        curve_layout = QtWidgets.QHBoxLayout()
        self.curve_list = QtWidgets.QListWidget()
        self.curve_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.curve_list.itemSelectionChanged.connect(self.on_curve_selection_changed)
        curve_layout.addWidget(QtWidgets.QLabel("Available Curves:"))
        curve_layout.addWidget(self.curve_list)

        self.plot_btn = QtWidgets.QPushButton("Plot Selected Curves")
        self.plot_btn.clicked.connect(self.plot_curves)
        self.plot_btn.setEnabled(False)
        curve_layout.addWidget(self.plot_btn)

        layout.addLayout(curve_layout)

        # Matplotlib figure area
        self.figure = plt.Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label)

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
                self.update_curve_list()
                self.calc_shale_btn.setEnabled(True)
                self.calc_porosity_btn.setEnabled(True)
                self.plot_btn.setEnabled(True)
                self.status_label.setText(f"Selected well: {well_name}")
            else:
                self.status_label.setText("Well not found")
        else:
            self.current_well = None
            self.curve_list.clear()
            self.calc_shale_btn.setEnabled(False)
            self.calc_porosity_btn.setEnabled(False)
            self.plot_btn.setEnabled(False)

    def update_curve_list(self):
        """Update the curve list widget."""
        self.curve_list.clear()
        if self.current_well:
            for curve_name in self.current_well.get_curve_names():
                item = QtWidgets.QListWidgetItem(curve_name)
                item.setToolTip(f"{curve_name}: {self.current_well.descriptions.get(curve_name, 'No description')}")
                self.curve_list.addItem(item)

    def on_curve_selection_changed(self):
        """Handle curve selection changes."""
        selected_curves = [item.text() for item in self.curve_list.selectedItems()]
        self.plot_btn.setEnabled(len(selected_curves) > 0)

    def plot_curves(self):
        """Plot selected curves."""
        if not self.current_well:
            return

        selected_curves = [item.text() for item in self.curve_list.selectedItems()]
        if not selected_curves:
            return

        self.figure.clear()
        axes = self.figure.subplots(len(selected_curves), 1, sharex=True)

        if len(selected_curves) == 1:
            axes = [axes]

        depth_curve = self.current_well._find_depth_curve()
        depth = self.current_well.get_curve_data(depth_curve) if depth_curve else np.arange(len(self.current_well.data))

        for i, curve_name in enumerate(selected_curves):
            data = self.current_well.get_curve_data(curve_name)
            if data is not None:
                axes[i].plot(data, depth)
                axes[i].set_ylabel(f"{curve_name}\n({self.current_well.units.get(curve_name, 'unitless')})")
                axes[i].grid(True, alpha=0.3)
                axes[i].invert_yaxis()

        axes[-1].set_xlabel("Value")
        self.figure.suptitle(f"Well Log Curves - {self.current_well.name}")
        self.figure.tight_layout()
        self.canvas.draw()
        self.status_label.setText(f"Plotted {len(selected_curves)} curves")

    def calculate_shale_volume(self):
        """Calculate and display shale volume."""
        if not self.current_well:
            return

        vsh = self.current_well.calculate_shale_volume()
        if vsh is None:
            self.status_label.setText("GR curve not found for shale volume calculation")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        depth_curve = self.current_well._find_depth_curve()
        depth = self.current_well.get_curve_data(depth_curve) if depth_curve else np.arange(len(vsh))

        ax.plot(vsh, depth, 'g-', linewidth=2, label='Shale Volume')
        ax.set_xlabel('Shale Volume (Vsh)')
        ax.set_ylabel('Depth')
        ax.set_title(f'Shale Volume - {self.current_well.name}')
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()
        ax.legend()

        self.figure.tight_layout()
        self.canvas.draw()
        self.status_label.setText("Shale volume calculated and plotted")

    def calculate_porosity(self):
        """Calculate and display porosity."""
        if not self.current_well:
            return

        phi = self.current_well.calculate_porosity()
        if phi is None:
            self.status_label.setText("RHOB curve not found for porosity calculation")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        depth_curve = self.current_well._find_depth_curve()
        depth = self.current_well.get_curve_data(depth_curve) if depth_curve else np.arange(len(phi))

        ax.plot(phi, depth, 'b-', linewidth=2, label='Porosity')
        ax.set_xlabel('Porosity (Phi)')
        ax.set_ylabel('Depth')
        ax.set_title(f'Porosity - {self.current_well.name}')
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()
        ax.legend()

        self.figure.tight_layout()
        self.canvas.draw()
        self.status_label.setText("Porosity calculated and plotted")


class ViewToolbar(QtWidgets.QToolBar):
    """Toolbar for view operations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("View Tools")
        self.setup_tools()

    def setup_tools(self):
        """Set up toolbar actions."""
        # Add 3D view button
        self.add_3d_action = QtWidgets.QAction("3D View", self)
        self.add_3d_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        self.add_3d_action.triggered.connect(lambda: self.parent().add_view(ViewType.VIEW_3D))
        self.addAction(self.add_3d_action)

        # Add Map view button
        self.add_map_action = QtWidgets.QAction("Map View", self)
        self.add_map_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
        self.add_map_action.triggered.connect(lambda: self.parent().add_view(ViewType.VIEW_MAP))
        self.addAction(self.add_map_action)

        # Add Well Section view button
        self.add_section_action = QtWidgets.QAction("Well Section", self)
        self.add_section_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
        self.add_section_action.triggered.connect(lambda: self.parent().add_view(ViewType.VIEW_WELL_SECTION))
        self.addAction(self.add_section_action)

        self.addSeparator()

        # Close current view button
        self.close_view_action = QtWidgets.QAction("Close View", self)
        self.close_view_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogCloseButton))
        self.close_view_action.triggered.connect(lambda: self.parent().close_current_view())
        self.addAction(self.close_view_action)
