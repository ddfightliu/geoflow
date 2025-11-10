"""
geoflow.ui package.

This package exposes `create_application` at the package level so existing
imports like `from geoflow.ui import create_application` continue to work.
"""
from .app import create_application
from .workspace import WorkspaceState
from .window import GeoflowMainWindow
from .highlighters import PythonHighlighter, JSONHighlighter
from .views import ViewType, BaseViewWidget, View3DWidget, ViewMapWidget, ViewWellSectionWidget, ViewToolbar

__all__ = [
    "create_application",
    "WorkspaceState",
    "GeoflowMainWindow",
    "PythonHighlighter",
    "JSONHighlighter",
    "ViewType",
    "BaseViewWidget",
    "View3DWidget",
    "ViewMapWidget",
    "ViewWellSectionWidget",
    "ViewToolbar",
]
