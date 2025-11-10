import os
import time
from pathlib import Path

import pytest

from geoflow.ui import WorkspaceState, GeoflowMainWindow, create_application


@pytest.fixture()
def tmp_workspace(tmp_path, monkeypatch):
    # place workspace in temp dir
    wsfile = tmp_path / '.geoflow_workspace.json'
    monkeypatch.chdir(tmp_path)
    yield wsfile


def test_autosave_and_restore(tmp_workspace):
    # create app headless
    app, win = create_application(argv=[], headless=True)

    # ensure no workspace exists
    if tmp_workspace.exists():
        tmp_workspace.unlink()

    # open a couple of tabs (simulate user)
    win.open_view({'title': 'T1', 'content': 'hello'})
    win.open_view({'title': 'T2', 'content': 'world'})

    # trigger autosave directly
    win.autosave()

    assert tmp_workspace.exists(), 'workspace file should be written by autosave'

    # create a new window bound to same workspace to test restore
    # we create a fresh WorkspaceState that points to the same file
    ws = WorkspaceState(path=tmp_workspace)
    app2 = None
    try:
        app2 = GeoflowMainWindow(workspace=ws)
        # restore_ui_from_workspace is called during init; check tabs
        titles = [app2.tabs.tabText(i) for i in range(app2.tabs.count())]
        assert 'T1' in titles and 'T2' in titles
    finally:
        # cleanup Qt objects (in headless mode, not showing)
        if app2 is not None:
            app2.deleteLater()
