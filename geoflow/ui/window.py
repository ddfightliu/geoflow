"""
Main window implementation.

This module contains the main window class for the geoflow application.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QThread, QObject, Signal

from .highlighters import PythonHighlighter, JSONHighlighter
from .workspace import WorkspaceState
from .views import ViewType, BaseViewWidget, View3DWidget, ViewMapWidget, ViewWellSectionWidget, ViewToolbar


AUTOSAVE_INTERVAL_MS = 5000


class GeoflowMainWindow(QtWidgets.QMainWindow):
    def __init__(self, workspace: WorkspaceState | None = None):
        super().__init__()
        self.workspace = workspace or WorkspaceState()
        self.setWindowTitle('geoflow')
        self.resize(1200, 800)
        self.setFont(QtGui.QFont('Segoe UI', 10))


        # Main horizontal splitter: activity bar, sidebar, editor
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # Activity bar (far left, narrow)
        self.activity_bar = QtWidgets.QFrame()
        self.activity_bar.setFixedWidth(50)
        activity_layout = QtWidgets.QVBoxLayout(self.activity_bar)
        activity_layout.setContentsMargins(0, 0, 0, 0)
        activity_layout.setSpacing(0)

        # Explorer button
        self.explorer_btn = QtWidgets.QPushButton()
        self.explorer_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
        self.explorer_btn.setToolTip("Explorer")
        self.explorer_btn.setCheckable(True)
        self.explorer_btn.setChecked(True)
        self.explorer_btn.clicked.connect(self.toggle_sidebar)
        activity_layout.addWidget(self.explorer_btn)

        # Placeholder for Search button
        search_btn = QtWidgets.QPushButton()
        search_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))  # Placeholder icon
        search_btn.setToolTip("Search")
        activity_layout.addWidget(search_btn)

        # Placeholder for Source Control button
        sc_btn = QtWidgets.QPushButton()
        sc_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))  # Placeholder icon
        sc_btn.setToolTip("Source Control")
        activity_layout.addWidget(sc_btn)

        activity_layout.addStretch()

        # Sidebar splitter: left sidebar and editor area
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Left sidebar (tree)
        self.left = QtWidgets.QFrame()
        self.left.setMinimumWidth(200)
        left_layout = QtWidgets.QVBoxLayout(self.left)
        left_label = QtWidgets.QLabel('Project')
        left_layout.addWidget(left_label)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.tree.itemDoubleClicked.connect(self.open_file_from_tree)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        left_layout.addWidget(self.tree)

        # Editor area (tabs)
        editor = QtWidgets.QWidget()
        editor_layout = QtWidgets.QVBoxLayout(editor)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        editor_layout.addWidget(self.tabs)

        splitter.addWidget(self.left)
        splitter.addWidget(editor)
        splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, True)  # sidebar collapsible
        splitter.setCollapsible(1, False)  # editor not collapsible

        main_splitter.addWidget(self.activity_bar)
        main_splitter.addWidget(splitter)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setCollapsible(0, False)  # activity bar not collapsible
        main_splitter.setCollapsible(1, False)  # splitter not collapsible

        # Bottom panel (dock widget for Output/Terminal)
        self.bottom_panel = QtWidgets.QDockWidget("Output")
        self.bottom_panel.setWidget(QtWidgets.QTextEdit())
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.bottom_panel)

        # Status bar
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage('Ready')

        # Autosave timer
        self.autosave_timer = QtCore.QTimer(self)
        self.autosave_timer.setInterval(AUTOSAVE_INTERVAL_MS)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start()

        # Hook close event to save state
        self._closing = False

        # List to keep track of highlighters for theme updates
        self.highlighters = []

        # List to keep track of view widgets
        self.view_widgets: List[BaseViewWidget] = []

        # Load theme (stylesheet) if available
        self._themes_dir = Path(__file__).parent / 'themes'
        self._current_theme = self.workspace.state.get('layout', {}).get('theme', 'dark')
        self.apply_theme(self._current_theme)

        # File menu
        file_menu = self.menuBar().addMenu('File')
        new_project_action = QtGui.QAction('New Project', self)
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)

        file_menu.addSeparator()

        new_action = QtGui.QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QtGui.QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QtGui.QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QtGui.QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = self.menuBar().addMenu('View')
        theme_menu = view_menu.addMenu('Theme')
        for theme_name in self.available_themes():
            action = QtGui.QAction(theme_name, self)
            action.setCheckable(True)
            action.setChecked(theme_name == self._current_theme)
            action.triggered.connect(lambda checked, tn=theme_name: self.set_theme(tn))
            theme_menu.addAction(action)

        view_menu.addSeparator()

        # Add view creation actions
        add_3d_action = QtGui.QAction('New 3D View', self)
        add_3d_action.setShortcut('Ctrl+Shift+3')
        add_3d_action.triggered.connect(lambda: self.add_view(ViewType.VIEW_3D))
        view_menu.addAction(add_3d_action)

        add_map_action = QtGui.QAction('New Map View', self)
        add_map_action.setShortcut('Ctrl+Shift+M')
        add_map_action.triggered.connect(lambda: self.add_view(ViewType.VIEW_MAP))
        view_menu.addAction(add_map_action)

        add_section_action = QtGui.QAction('New Well Section View', self)
        add_section_action.setShortcut('Ctrl+Shift+W')
        add_section_action.triggered.connect(lambda: self.add_view(ViewType.VIEW_WELL_SECTION))
        view_menu.addAction(add_section_action)

        view_menu.addSeparator()

        sidebar_toggle = QtGui.QAction('Toggle Sidebar', self)
        sidebar_toggle.setCheckable(True)
        sidebar_toggle.setChecked(True)
        sidebar_toggle.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(sidebar_toggle)

        bottom_toggle = QtGui.QAction('Toggle Bottom Panel', self)
        bottom_toggle.setCheckable(True)
        bottom_toggle.setChecked(True)
        bottom_toggle.triggered.connect(self.toggle_bottom_panel)
        view_menu.addAction(bottom_toggle)

        # Tab shortcuts are handled by QTabWidget by default (Ctrl+Tab)

        # Populate UI from workspace
        self.restore_ui_from_workspace()

    def restore_ui_from_workspace(self):
        if self.workspace.load():
            st = self.workspace.state
            # populate tree and tabs from saved state (best-effort)
            self.populate_tree()
            for v in st.get('open_views', []):
                if v.get('type') == 'view':
                    view_type_str = v.get('view_type')
                    if view_type_str == '3D':
                        self.add_view(ViewType.VIEW_3D)
                    elif view_type_str == 'Map':
                        self.add_view(ViewType.VIEW_MAP)
                    elif view_type_str == 'Well Section':
                        self.add_view(ViewType.VIEW_WELL_SECTION)
                else:
                    self.open_view(v)
            self.status.showMessage('Restored session')
        else:
            # default UI
            self.populate_tree()
            self.open_view({'title': 'Welcome', 'content': 'Welcome to geoflow'})

    def populate_tree(self):
        self.tree.clear()
        # Add project root
        root = QtWidgets.QTreeWidgetItem([self.workspace.project_path.name])
        root.setIcon(0, self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
        root.setData(0, QtCore.Qt.UserRole, str(self.workspace.project_path))
        self.tree.addTopLevelItem(root)
        # Recursively add files and directories
        self._populate_tree_recursive(self.workspace.project_path, root)

    def _populate_tree_recursive(self, path: Path, parent_item: QtWidgets.QTreeWidgetItem):
        """Recursively populate the tree with files and directories."""
        try:
            for item_path in sorted(path.iterdir()):
                if item_path.name.startswith('.'):
                    continue  # Skip hidden files/directories
                tree_item = QtWidgets.QTreeWidgetItem([item_path.name])
                tree_item.setData(0, QtCore.Qt.UserRole, str(item_path))
                if item_path.is_dir():
                    tree_item.setIcon(0, self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
                    parent_item.addChild(tree_item)
                    self._populate_tree_recursive(item_path, tree_item)
                else:
                    tree_item.setIcon(0, self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                    parent_item.addChild(tree_item)
        except PermissionError:
            pass  # Skip directories we can't read

    def open_view(self, view_data):
        title = view_data['title']
        content = view_data['content']
        editor = QtWidgets.QPlainTextEdit()
        editor.setPlainText(content)

        # Determine language from file extension and apply syntax highlighting
        colors = self.get_syntax_colors(self._current_theme)
        if title.endswith('.py'):
            highlighter = PythonHighlighter(editor.document(), colors)
        elif title.endswith('.json'):
            highlighter = JSONHighlighter(editor.document(), colors)
        else:
            highlighter = None

        if highlighter:
            self.highlighters.append(highlighter)

        self.tabs.addTab(editor, title)

    def autosave(self):
        if self._closing:
            return
        try:
            self.workspace.state['open_views'] = []
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                title = self.tabs.tabText(i)
                if isinstance(w, QtWidgets.QPlainTextEdit):
                    view_data = {
                        'type': 'text',
                        'title': title,
                        'content': w.toPlainText()[:100000],
                    }
                else:
                    # Assume it's a view widget; save type if available
                    view_type = getattr(w, 'view_type', 'unknown')
                    if isinstance(view_type, ViewType):
                        view_type_str = view_type.value
                    else:
                        view_type_str = str(view_type)
                    view_data = {
                        'type': 'view',
                        'title': title,
                        'view_type': view_type_str,
                        'content': None,  # Views don't save content this way
                    }
                self.workspace.state['open_views'].append(view_data)
            self.workspace.state['last_opened'] = None
            # persist current theme
            if 'layout' not in self.workspace.state:
                self.workspace.state['layout'] = {}
            self.workspace.state['layout']['theme'] = self._current_theme
            ok = self.workspace.save()
            if ok:
                self.status.showMessage('Workspace autosaved')
            else:
                self.status.showMessage('Autosave failed')
        except Exception as e:
            print('Autosave exception:', e)

    def closeEvent(self, event: QtGui.QCloseEvent):
        # mark closing and save synchronously
        self._closing = True
        self.autosave_timer.stop()
        try:
            self.autosave()
        except Exception:
            pass
        super().closeEvent(event)

    def available_themes(self):
        out = []
        if self._themes_dir.exists():
            for p in self._themes_dir.glob('*.qss'):
                out.append(p.stem)
        return sorted(out)

    def get_syntax_colors(self, theme_name: str) -> Dict[str, str]:
        # Default dark theme colors (based on VSCode dark)
        colors = {
            'keyword': '#569cd6',
            'string': '#ce9178',
            'comment': '#6a9955',
            'number': '#b5cea8',
            'function': '#dcdcaa',
            'key': '#9cdcfe',
            'boolean': '#569cd6'
        }

        # Light theme adjustments
        if theme_name == 'light':
            colors.update({
                'keyword': '#0000ff',
                'string': '#008000',
                'comment': '#008000',
                'number': '#09885a',
                'function': '#795e26',
                'key': '#0000ff',
                'boolean': '#0000ff'
            })

        # High contrast theme
        elif theme_name == 'high_contrast':
            colors.update({
                'keyword': '#ffff00',
                'string': '#ff00ff',
                'comment': '#00ff00',
                'number': '#00ffff',
                'function': '#ff8000',
                'key': '#ffff00',
                'boolean': '#ffff00'
            })

        # Aqua theme (light-like)
        elif theme_name == 'Aqua':
            colors.update({
                'keyword': '#0000ff',
                'string': '#008000',
                'comment': '#008000',
                'number': '#09885a',
                'function': '#795e26',
                'key': '#0000ff',
                'boolean': '#0000ff'
            })

        # MacOS theme (light-like)
        elif theme_name == 'MacOS':
            colors.update({
                'keyword': '#0000ff',
                'string': '#008000',
                'comment': '#008000',
                'number': '#09885a',
                'function': '#795e26',
                'key': '#0000ff',
                'boolean': '#0000ff'
            })

        # Ubuntu theme (dark)
        elif theme_name == 'Ubuntu':
            pass  # use default dark

        # ManjaroMix theme (dark)
        elif theme_name == 'ManjaroMix':
            pass  # use default dark

        # NeonButtons theme (dark)
        elif theme_name == 'NeonButtons':
            colors.update({
                'keyword': '#00ffff',
                'string': '#ff00ff',
                'comment': '#00ff00',
                'number': '#ffff00',
                'function': '#ff8000',
                'key': '#00ffff',
                'boolean': '#00ffff'
            })

        # ElegantDark theme (dark)
        elif theme_name == 'ElegantDark':
            pass  # use default dark

        # MaterialDark theme (dark)
        elif theme_name == 'MaterialDark':
            pass  # use default dark

        # AMOLED theme (dark)
        elif theme_name == 'AMOLED':
            pass  # use default dark

        # ConsoleStyle theme (dark)
        elif theme_name == 'ConsoleStyle':
            pass  # use default dark

        return colors

    def apply_theme(self, name: str):
        path = self._themes_dir / f'{name}.qss'
        if path.exists():
            try:
                self.setStyleSheet(path.read_text(encoding='utf8'))
                self._current_theme = name
            except Exception as e:
                print('Failed to apply theme', name, e)

    def set_theme(self, name: str):
        self.apply_theme(name)
        # Update syntax highlighters with new colors
        new_colors = self.get_syntax_colors(name)
        for highlighter in self.highlighters:
            highlighter.update_colors(new_colors)
        # update menu checks
        for ma in self.menuBar().actions():
            if ma.menu():
                for a in ma.menu().actions():
                    if a.menu():
                        for sub in a.menu().actions():
                            sub.setChecked(sub.text() == name)

    def toggle_sidebar(self):
        self.left.setVisible(self.explorer_btn.isChecked())

    def show_tree_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if item:
            menu = QtWidgets.QMenu(self)
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda: self.open_file_from_tree(item))
            # Add "Load Well" action for LAS files
            if item.text(0).endswith('.las'):
                load_well_action = menu.addAction("Load Well")
                load_well_action.triggered.connect(lambda: self.load_well_from_tree(item))
            menu.exec(self.tree.mapToGlobal(pos))

    def open_file_from_tree(self, item):
        """Open a file from the project tree in a new tab."""
        file_path_str = item.data(0, QtCore.Qt.UserRole)
        if file_path_str:
            file_path = Path(file_path_str)
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf8')
                    title = file_path.name
                    self.open_view({'title': title, 'content': content})
                    self.status.showMessage(f'Opened {title}')
                except Exception as e:
                    self.status.showMessage(f'Failed to open file: {e}')
            else:
                self.status.showMessage('Selected item is not a file')
        else:
            self.status.showMessage('No file path associated with item')

    def load_well_from_tree(self, item):
        """Load a well from the project tree."""
        file_path_str = item.data(0, QtCore.Qt.UserRole)
        if file_path_str:
            file_path = Path(file_path_str)
            if file_path.exists() and file_path.is_file():
                # Find the Well Section view and load the well there
                for widget in self.view_widgets:
                    if isinstance(widget, ViewWellSectionWidget):
                        well_name = widget.well_manager.load_well(str(file_path))
                        if well_name:
                            widget.well_combo.addItem(well_name)
                            widget.well_combo.setCurrentText(well_name)
                            self.status.showMessage(f"Loaded well: {well_name}")
                            return
                self.status.showMessage("No Well Section view open. Please open a Well Section view first.")
            else:
                self.status.showMessage(f"File not found: {file_path}")
        else:
            self.status.showMessage('No file path associated with item')

    def close_tab(self, index):
        # Remove the highlighter if it exists
        if index < len(self.highlighters):
            self.highlighters.pop(index)
        # Remove the view widget if it exists
        if index < len(self.view_widgets):
            self.view_widgets.pop(index)
        self.tabs.removeTab(index)

    def add_view(self, view_type: ViewType):
        """Add a new view of the specified type."""
        if view_type == ViewType.VIEW_3D:
            view_widget = View3DWidget()
        elif view_type == ViewType.VIEW_MAP:
            view_widget = ViewMapWidget()
        elif view_type == ViewType.VIEW_WELL_SECTION:
            view_widget = ViewWellSectionWidget()
        else:
            return

        self.view_widgets.append(view_widget)
        self.tabs.addTab(view_widget, view_widget.windowTitle())
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        self.status.showMessage(f'Opened {view_type.value} view')

    def close_current_view(self):
        """Close the currently active view."""
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)

    def new_file(self):
        # Placeholder: create new tab
        self.open_view({'title': 'untitled', 'content': ''})

    def open_file(self):
        # Placeholder: open file dialog
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            try:
                content = Path(file_path).read_text(encoding='utf8')
                title = Path(file_path).name
                self.open_view({'title': title, 'content': content})
            except Exception as e:
                self.status.showMessage(f'Failed to open file: {e}')

    def save_file(self):
        # Placeholder: save current tab
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            w = self.tabs.widget(current_index)
            content = w.toPlainText()
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File")
            if file_path:
                try:
                    Path(file_path).write_text(content, encoding='utf8')
                    self.status.showMessage('File saved')
                except Exception as e:
                    self.status.showMessage(f'Failed to save file: {e}')

    def toggle_bottom_panel(self):
        self.bottom_panel.setVisible(not self.bottom_panel.isVisible())

    def new_project(self):
        """Create a new project."""
        # Select directory for new project
        project_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if not project_dir:
            return

        project_path = Path(project_dir)

        # Create project_info.json
        project_info = {
            "project_name": project_path.name,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }
        project_info_path = project_path / 'project_info.json'
        try:
            with open(project_info_path, 'w', encoding='utf8') as f:
                json.dump(project_info, f, indent=2)
        except Exception as e:
            self.status.showMessage(f'Failed to create project_info.json: {e}')
            return

        # Switch workspace to new project
        self.workspace = WorkspaceState(project_path)
        self.workspace.load()  # Load existing workspace if any

        # Reload UI
        self.populate_tree()
        self.tabs.clear()
        self.highlighters.clear()
        self.view_widgets.clear()
        self.open_view({'title': 'Welcome', 'content': f'Welcome to project: {project_path.name}'})
        self.status.showMessage(f'New project created: {project_path.name}')
