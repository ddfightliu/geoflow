import importlib
import pytest


def test_import_main_callable():
    mod = importlib.import_module('geoflow.app')
    assert hasattr(mod, 'main') and callable(mod.main)


@pytest.mark.skipif(importlib.util.find_spec('PySide6') is None, reason='PySide6 not installed')
def test_instantiate_mainwindow(qtbot=None):
    # Import locally to ensure the skipif check runs first
    from PySide6 import QtWidgets
    from geoflow.ui import GeoflowMainWindow, ViewType

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = GeoflowMainWindow()
    # basic sanity: object created and has a title
    assert win.windowTitle() == 'geoflow'

    # Test adding views
    win.add_view(ViewType.VIEW_3D)
    assert win.tabs.count() > 0
    assert isinstance(win.tabs.widget(0), QtWidgets.QWidget)  # View widget

    win.add_view(ViewType.VIEW_MAP)
    win.add_view(ViewType.VIEW_WELL_SECTION)
    assert win.tabs.count() == 4  # 1 Welcome + 3 views

    # Test close tab
    win.close_tab(0)
    assert win.tabs.count() == 3

    win.close()
