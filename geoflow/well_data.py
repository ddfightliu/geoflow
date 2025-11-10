"""
Well logging data processing and interpretation module.

This module provides functionality for loading, processing, and interpreting
well logging data from LAS files and other formats.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import lasio


class WellLogData:
    """Class to handle well logging data."""

    def __init__(self, name: str = "Unknown Well"):
        self.name = name
        self.data: Optional[pd.DataFrame] = None
        self.curves: Dict[str, np.ndarray] = {}
        self.units: Dict[str, str] = {}
        self.descriptions: Dict[str, str] = {}

    def load_from_las(self, file_path: str) -> bool:
        """Load well data from LAS file."""
        try:
            las = lasio.read(file_path)
            self.name = las.well.WELL.value if hasattr(las.well, 'WELL') else Path(file_path).stem

            # Extract data
            data_dict = {}
            for curve in las.curves:
                curve_name = curve.mnemonic
                data_dict[curve_name] = curve.data
                self.units[curve_name] = curve.unit if curve.unit else ""
                self.descriptions[curve_name] = curve.descr if curve.descr else ""

            self.data = pd.DataFrame(data_dict)
            self.curves = {k: v for k, v in data_dict.items() if v is not None}
            return True
        except Exception as e:
            print(f"Error loading LAS file {file_path}: {e}")
            return False

    def get_curve_names(self) -> List[str]:
        """Get list of available curve names."""
        return list(self.curves.keys())

    def get_curve_data(self, curve_name: str) -> Optional[np.ndarray]:
        """Get data for a specific curve."""
        return self.curves.get(curve_name)

    def calculate_shale_volume(self, gr_curve: str = "GR", gr_clean: float = 30.0,
                              gr_shale: float = 150.0) -> Optional[np.ndarray]:
        """Calculate shale volume using gamma ray log."""
        if gr_curve not in self.curves:
            return None

        gr = self.curves[gr_curve]
        vsh = (gr - gr_clean) / (gr_shale - gr_clean)
        vsh = np.clip(vsh, 0, 1)  # Clip to [0, 1]
        return vsh

    def calculate_porosity(self, density_curve: str = "RHOB", fluid_density: float = 1.0,
                          matrix_density: float = 2.65) -> Optional[np.ndarray]:
        """Calculate porosity from density log."""
        if density_curve not in self.curves:
            return None

        rhob = self.curves[density_curve]
        phi = (matrix_density - rhob) / (matrix_density - fluid_density)
        phi = np.clip(phi, 0, 1)  # Clip to [0, 1]
        return phi

    def plot_curves(self, curve_names: List[str], figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
        """Plot selected curves."""
        if self.data is None or self.data.empty:
            return None

        fig, axes = plt.subplots(len(curve_names), 1, figsize=figsize, sharex=True)
        if len(curve_names) == 1:
            axes = [axes]

        depth_curve = self._find_depth_curve()
        depth = self.curves.get(depth_curve, np.arange(len(self.data)))

        for i, curve_name in enumerate(curve_names):
            if curve_name in self.curves:
                data = self.curves[curve_name]
                axes[i].plot(data, depth)
                axes[i].set_ylabel(f"{curve_name}\n({self.units.get(curve_name, 'unitless')})")
                axes[i].grid(True, alpha=0.3)
                axes[i].invert_yaxis()  # Depth increases downward

        axes[-1].set_xlabel("Value")
        fig.suptitle(f"Well Log Curves - {self.name}")
        plt.tight_layout()
        return fig

    def _find_depth_curve(self) -> Optional[str]:
        """Find the depth curve in the data."""
        depth_candidates = ['DEPT', 'DEPTH', 'MD', 'TVD']
        for candidate in depth_candidates:
            if candidate in self.curves:
                return candidate
        return None


class WellDataManager:
    """Manager class for handling multiple wells."""

    def __init__(self):
        self.wells: Dict[str, WellLogData] = {}

    def load_well(self, file_path: str) -> Optional[str]:
        """Load a well from file and return its name."""
        well = WellLogData()
        if well.load_from_las(file_path):
            self.wells[well.name] = well
            return well.name
        return None

    def get_well(self, name: str) -> Optional[WellLogData]:
        """Get a well by name."""
        return self.wells.get(name)

    def get_well_names(self) -> List[str]:
        """Get list of loaded well names."""
        return list(self.wells.keys())
