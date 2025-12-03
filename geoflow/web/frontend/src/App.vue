<template>
  <div style="display: flex; flex-direction: column; height: 100vh;">
    <MenuBar @command-executed="handleCommand" />
    <div style="display: flex; flex: 1;">
      <ActivityBar
        :active-panel="activePanel"
        @panel-change="setActivePanel"
      />
    <div
      v-if="sidebarVisible"
      ref="sidebar"
      :style="{ width: sidebarWidth + 'px', backgroundColor: '#252526', borderRight: '1px solid #3e3e42', position: 'relative' }"
    >
      <div
        class="resize-handle"
        @mousedown="startResize"
        style="position: absolute; right: 0; top: 0; bottom: 0; width: 5px; cursor: ew-resize; background-color: transparent;"
      ></div>
      <ExplorerPanel
        v-if="activePanel === 'explorer'"
        :project-data="projectData"
        @file-open="openFile"
        @project-loaded="onProjectLoaded"
      />
      <SearchPanel
        v-else-if="activePanel === 'search'"
        @file-open="openFile"
      />
      <SourceControlPanel
        v-else-if="activePanel === 'source-control'"
      />
      <ExtensionsPanel
        v-else-if="activePanel === 'extensions'"
      />
      <ProblemsPanel
        v-else-if="activePanel === 'problems'"
        @file-open="openFile"
      />
    </div>
    <div style="flex: 1; display: flex; flex-direction: column;">
      <div style="display: flex; background-color: #2d2d30;">
        <div
          v-for="file in openFiles"
          :key="file"
          :style="{
            padding: '8px 16px',
            backgroundColor: currentView === file ? '#37373d' : '#2d2d30',
            cursor: 'pointer',
            borderRight: '1px solid #3e3e42'
          }"
          @click="setCurrentView(file)"
        >
          {{ file }}
          <span
            style="margin-left: 8px; cursor: pointer;"
            @click.stop="closeFile(file)"
          >
            ×
          </span>
        </div>
      </div>
      <div style="flex: 1; overflow: auto;">
        <Views v-if="currentView === 'welcome'" />
        <Editor v-else :file-name="currentView" :settings="editorSettings" />
      </div>
      </div>
    </div>
    <CommandPalette
      :show="showCommandPalette"
      @close="showCommandPalette = false"
      @command-executed="handleCommand"
    />
    <SettingsDialog
      :show="showSettings"
      @close="showSettings = false"
      @settings-changed="handleSettingsChange"
    />
  </div>
</template>

<script>
import MenuBar from './components/MenuBar.vue'
import ActivityBar from './components/ActivityBar.vue'
import ExplorerPanel from './components/ExplorerPanel.vue'
import SearchPanel from './components/SearchPanel.vue'
import SourceControlPanel from './components/SourceControlPanel.vue'
import ExtensionsPanel from './components/ExtensionsPanel.vue'
import ProblemsPanel from './components/ProblemsPanel.vue'
import Editor from './components/Editor.vue'
import Views from './components/Views.vue'
import CommandPalette from './components/CommandPalette.vue'
import SettingsDialog from './components/SettingsDialog.vue'

export default {
  name: 'App',
  components: {
    MenuBar,
    ActivityBar,
    ExplorerPanel,
    SearchPanel,
    SourceControlPanel,
    ExtensionsPanel,
    ProblemsPanel,
    Editor,
    Views,
    CommandPalette,
    SettingsDialog
  },
  data() {
    return {
      currentView: 'welcome',
      openFiles: [],
      projectData: null,
      activePanel: 'explorer',
      sidebarVisible: true,
      sidebarWidth: 250,
      isResizing: false,
      showCommandPalette: false,
      showSettings: false,
      editorSettings: {
        theme: 'vs-dark',
        fontSize: 14,
        wordWrap: true
      }
    }
  },
  mounted() {
    this.loadProject()
    this.loadSettings()
    this.setupKeyboardShortcuts()
  },
  methods: {
    async loadProject() {
      // Project loading is now handled by ExplorerPanel component
      // This method can be kept for backward compatibility or removed
    },
    loadSettings() {
      const settings = JSON.parse(localStorage.getItem('geoflow-settings') || '{}')
      this.editorSettings = {
        theme: settings.theme || 'vs-dark',
        fontSize: settings.fontSize || 14,
        wordWrap: settings.wordWrap !== false
      }
    },
    setupKeyboardShortcuts() {
      document.addEventListener('keydown', (event) => {
        if (event.ctrlKey && event.shiftKey && event.key === 'P') {
          event.preventDefault()
          this.showCommandPalette = true
        }
      })
      document.addEventListener('mousemove', this.handleMouseMove)
      document.addEventListener('mouseup', this.handleMouseUp)
    },
    openFile(fileName) {
      if (!this.openFiles.includes(fileName)) {
        this.openFiles.push(fileName)
      }
      this.currentView = fileName
    },
    closeFile(fileName) {
      const index = this.openFiles.indexOf(fileName)
      if (index > -1) {
        this.openFiles.splice(index, 1)
        if (this.currentView === fileName) {
          this.currentView = this.openFiles.length > 0 ? this.openFiles[0] : 'welcome'
        }
      }
    },
    setCurrentView(view) {
      this.currentView = view
    },
    setActivePanel(panelId) {
      if (this.activePanel === panelId) {
        this.sidebarVisible = !this.sidebarVisible
      } else {
        this.activePanel = panelId
        this.sidebarVisible = true
      }
    },
    handleCommand(command) {
      switch (command.id) {
        case 'open-file':
          this.openFileDialog()
          break
        case 'new-file':
          this.createNewFile()
          break
        case 'new-project':
          this.createNewProject()
          break
        case 'save-file':
          this.saveCurrentFile()
          break
        case 'save-as':
          this.saveFileAs()
          break
        case 'save-all':
          this.saveAllFiles()
          break
        case 'close-file':
          if (this.currentView !== 'welcome') {
            this.closeFile(this.currentView)
          }
          break
        case 'undo':
          this.undoAction()
          break
        case 'redo':
          this.redoAction()
          break
        case 'cut':
          this.cutAction()
          break
        case 'copy':
          this.copyAction()
          break
        case 'paste':
          this.pasteAction()
          break
        case 'find':
          this.findAction()
          break
        case 'replace':
          this.replaceAction()
          break
        case 'toggle-sidebar':
          this.sidebarVisible = !this.sidebarVisible
          break
        case 'command-palette':
          this.showCommandPalette = true
          break
        case 'settings':
          this.showSettings = true
          break
        case 'reload-window':
          window.location.reload()
          break
      }
    },
    handleSettingsChange(settings) {
      this.editorSettings = {
        theme: settings.theme || this.editorSettings.theme,
        fontSize: settings.fontSize || this.editorSettings.fontSize,
        wordWrap: settings.wordWrap !== undefined ? settings.wordWrap : this.editorSettings.wordWrap
      }
    },
    openFileDialog() {
      // Create a hidden file input
      const input = document.createElement('input')
      input.type = 'file'
      input.multiple = true
      input.onchange = (e) => {
        const files = Array.from(e.target.files)
        files.forEach(file => {
          const reader = new FileReader()
          reader.onload = (event) => {
            this.openFile(file.name, event.target.result)
          }
          reader.readAsText(file)
        })
      }
      input.click()
    },
    createNewFile() {
      const fileName = prompt('Enter file name:')
      if (fileName) {
        this.openFile(fileName, '')
      }
    },
    async createNewProject() {
      const projectName = prompt('Enter project name:')
      if (projectName) {
        try {
          const response = await fetch('/api/project/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: projectName })
          })
          if (response.ok) {
            const result = await response.json()
            alert(result.message)
            // Reload project data
            this.loadProject()
          } else {
            alert('Failed to create project')
          }
        } catch (error) {
          console.error('Project creation error:', error)
          alert('Error creating project')
        }
      }
    },
    async saveCurrentFile() {
      if (this.currentView !== 'welcome') {
        try {
          const response = await fetch(`/api/files/${this.currentView}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: this.getCurrentFileContent() })
          })
          if (response.ok) {
            alert('File saved successfully')
          } else {
            alert('Failed to save file')
          }
        } catch (error) {
          console.error('Save error:', error)
          alert('Error saving file')
        }
      }
    },
    saveFileAs() {
      const newFileName = prompt('Enter new file name:', this.currentView)
      if (newFileName && newFileName !== this.currentView) {
        // TODO: Implement save as logic
        alert(`Save as "${newFileName}" (placeholder)`)
      }
    },
    saveAllFiles() {
      // TODO: Implement save all logic
      alert('Save all files (placeholder)')
    },
    undoAction() {
      // TODO: Implement undo logic
      alert('Undo (placeholder)')
    },
    redoAction() {
      // TODO: Implement redo logic
      alert('Redo (placeholder)')
    },
    cutAction() {
      document.execCommand('cut')
    },
    copyAction() {
      document.execCommand('copy')
    },
    pasteAction() {
      document.execCommand('paste')
    },
    findAction() {
      // TODO: Implement find logic
      alert('Find (placeholder)')
    },
    replaceAction() {
      // TODO: Implement replace logic
      alert('Replace (placeholder)')
    },
    getCurrentFileContent() {
      // This would need to be implemented to get content from the editor
      // For now, return empty string as placeholder
      return ''
    },
    startResize(event) {
      this.isResizing = true
      this.initialX = event.clientX
      this.initialWidth = this.sidebarWidth
      event.preventDefault()
    },
    handleMouseMove(event) {
      if (this.isResizing) {
        const deltaX = event.clientX - this.initialX
        const newWidth = Math.max(150, Math.min(600, this.initialWidth + deltaX))
        this.sidebarWidth = newWidth
      }
    },
    handleMouseUp() {
      this.isResizing = false
    },
    onProjectLoaded(data) {
      this.projectData = data
    }
  }
}
</script>

<style scoped>
/* Add any scoped styles here if needed */
</style>
