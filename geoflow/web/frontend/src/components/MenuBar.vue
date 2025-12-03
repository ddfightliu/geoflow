<template>
  <div class="menu-bar">
    <div class="menu-item" @click="toggleMenu('file')" :class="{ active: activeMenu === 'file' }">
      File
      <div v-if="activeMenu === 'file'" class="menu-dropdown">
        <div class="menu-option" @click="handleCommand('new-file')">New File</div>
        <div class="menu-option" @click="handleCommand('new-project')">New Project</div>
        <div class="menu-option" @click="handleCommand('open-file')">Open File</div>
        <div class="menu-separator"></div>
        <div class="menu-option" @click="handleCommand('save-file')">Save</div>
        <div class="menu-option" @click="handleCommand('save-as')">Save As...</div>
        <div class="menu-option" @click="handleCommand('save-all')">Save All</div>
        <div class="menu-separator"></div>
        <div class="menu-option" @click="handleCommand('close-file')">Close File</div>
      </div>
    </div>
    <div class="menu-item" @click="toggleMenu('edit')" :class="{ active: activeMenu === 'edit' }">
      Edit
      <div v-if="activeMenu === 'edit'" class="menu-dropdown">
        <div class="menu-option" @click="handleCommand('undo')">Undo</div>
        <div class="menu-option" @click="handleCommand('redo')">Redo</div>
        <div class="menu-separator"></div>
        <div class="menu-option" @click="handleCommand('cut')">Cut</div>
        <div class="menu-option" @click="handleCommand('copy')">Copy</div>
        <div class="menu-option" @click="handleCommand('paste')">Paste</div>
        <div class="menu-separator"></div>
        <div class="menu-option" @click="handleCommand('find')">Find</div>
        <div class="menu-option" @click="handleCommand('replace')">Replace</div>
      </div>
    </div>
    <div class="menu-item" @click="toggleMenu('view')" :class="{ active: activeMenu === 'view' }">
      View
      <div v-if="activeMenu === 'view'" class="menu-dropdown">
        <div class="menu-option" @click="handleCommand('toggle-sidebar')">Toggle Sidebar</div>
        <div class="menu-option" @click="handleCommand('command-palette')">Command Palette</div>
        <div class="menu-option" @click="handleCommand('settings')">Settings</div>
        <div class="menu-separator"></div>
        <div class="menu-option" @click="handleCommand('reload-window')">Reload Window</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MenuBar',
  emits: ['command-executed'],
  data() {
    return {
      activeMenu: null
    }
  },
  mounted() {
    document.addEventListener('click', this.closeMenu)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeMenu)
  },
  methods: {
    toggleMenu(menu) {
      this.activeMenu = this.activeMenu === menu ? null : menu
    },
    closeMenu(event) {
      if (!this.$el.contains(event.target)) {
        this.activeMenu = null
      }
    },
    handleCommand(commandId) {
      this.$emit('command-executed', { id: commandId })
      this.activeMenu = null
    }
  }
}
</script>

<style scoped>
.menu-bar {
  height: 30px;
  background-color: #2d2d30;
  border-bottom: 1px solid #3e3e42;
  display: flex;
  align-items: center;
  padding: 0 10px;
  user-select: none;
}

.menu-item {
  position: relative;
  padding: 0 12px;
  height: 100%;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #cccccc;
  font-size: 13px;
}

.menu-item:hover {
  background-color: #37373d;
}

.menu-item.active {
  background-color: #37373d;
}

.menu-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #252526;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  min-width: 180px;
  z-index: 1000;
}

.menu-option {
  padding: 8px 16px;
  cursor: pointer;
  color: #cccccc;
  font-size: 13px;
}

.menu-option:hover {
  background-color: #37373d;
}

.menu-separator {
  height: 1px;
  background-color: #3e3e42;
  margin: 4px 0;
}
</style>
