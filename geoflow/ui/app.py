"""
Application creation and management.

This module contains functions for creating and managing the PySide6 application.
"""

from PySide6 import QtWidgets

from .window import GeoflowMainWindow
from .workspace import WorkspaceState


def create_application(argv=None, headless: bool = False) -> QtWidgets.QApplication:
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(argv or [])
    workspace = WorkspaceState()
    win = GeoflowMainWindow(workspace=workspace)
    if not headless:
        win.show()
    return app, win
