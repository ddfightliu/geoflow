# Geoflow VSCode-like Improvements

## Phase 1: Core VSCode Features
- [ ] **Activity Bar Enhancements**
  - Add Search icon and panel
  - Add Source Control (Git) icon and panel
  - Add Extensions icon and panel
  - Add Debug icon and panel
  - Add Settings icon

- [ ] **Sidebar Improvements**
  - Make sidebar panels collapsible
  - Add Search panel with file/content search
  - Add Source Control panel with Git status
  - Add Extensions panel
  - Add Problems panel for errors/warnings

- [ ] **Command Palette**
  - Implement Ctrl+Shift+P command palette
  - Add common commands (open file, new file, etc.)
  - Add view switching commands

- [ ] **Settings & Preferences**
  - Add settings dialog
  - Support for user/workspace settings
  - Theme selection improvements

## Phase 2: Editor & Views
- [ ] **Split Editor Support**
  - Horizontal/vertical split panes
  - Drag and drop between panes

- [ ] **Better File Management**
  - Drag and drop files
  - Better context menus
  - File operations (rename, delete, etc.)

- [ ] **Enhanced Views**
  - Improve 3D view with better controls
  - Add more view types (seismic, cross-section)
  - Better view switching

## Phase 3: Development Tools
- [ ] **Integrated Terminal**
  - Add terminal panel
  - Support for multiple terminals
  - Command execution integration

- [ ] **Problems Panel**
  - Show Python errors/warnings
  - File parsing issues
  - Validation errors

- [ ] **Output Panel**
  - Build output
  - Command execution results
  - Debug output

## Phase 4: Web Version Improvements
- [ ] **Web Activity Bar**
  - Mirror desktop activity bar features

- [ ] **Web Sidebar Panels**
  - Add collapsible panels
  - Search functionality

- [ ] **Web Command Palette**
  - Keyboard shortcut support

- [ ] **Web Terminal**
  - Integrated web terminal

## Phase 5: Extensions & Customization
- [ ] **Extension Framework**
  - Plugin system for views
  - Custom tools and panels

- [ ] **Theme System**
  - More themes
  - Custom theme support

## Phase 1 Web: Core VSCode Features for Web Frontend
- [x] Create ActivityBar.vue component with icons for Explorer, Search, Source Control, Extensions, Problems, Settings
- [x] Rename Sidebar.vue to ExplorerPanel.vue and update for panel switching
- [x] Create SearchPanel.vue for file/content search
- [x] Create SourceControlPanel.vue for Git status
- [x] Create ExtensionsPanel.vue placeholder
- [x] Create ProblemsPanel.vue for errors/warnings
- [x] Create CommandPalette.vue modal with search and commands
- [x] Create SettingsDialog.vue modal with theme selection
- [x] Update App.vue to include activity bar and conditional sidebar panels
- [x] Add keyboard event listeners for Ctrl+Shift+P in App.vue
- [x] Update backend main.py with /api/search, /api/git-status, /api/settings endpoints
- [x] Test the implementation and update TODO.md

## Current Status
- Desktop version has basic VSCode-like layout
- Web version has basic editor functionality
- Implementing Phase 1 for web frontend
