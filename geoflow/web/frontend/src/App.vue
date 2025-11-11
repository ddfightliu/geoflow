<template>
  <div style="display: flex; height: 100vh;">
    <ActivityBar
      :active-panel="activePanel"
      @panel-change="setActivePanel"
    />
    <div v-if="sidebarVisible" style="width: 250px; background-color: #252526; border-right: 1px solid #3e3e42;">
      <ExplorerPanel
        v-if="activePanel === 'explorer'"
        :project-data="projectData"
        @file-open="openFile"
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
      try {
        const response = await fetch('/api/project')
        const data = await response.json()
        this.projectData = data
      } catch (error) {
        console.error('Failed to load project:', error)
      }
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
          // Implement file picker
          break
        case 'new-file':
          // Implement new file creation
          break
        case 'save-file':
          // Implement save current file
          break
        case 'close-file':
          if (this.currentView !== 'welcome') {
            this.closeFile(this.currentView)
          }
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
    }
  }
}
</script>

<style scoped>
/* Add any scoped styles here if needed */
</style>
