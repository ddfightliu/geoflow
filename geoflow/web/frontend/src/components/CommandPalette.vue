<template>
  <div v-if="show" class="command-palette-overlay" @click="close">
    <div class="command-palette" @click.stop>
      <div class="search-input">
        <i class="fas fa-search"></i>
        <input
          ref="searchInput"
          v-model="searchQuery"
          @input="filterCommands"
          @keydown="handleKeydown"
          placeholder="Type a command or search..."
          type="text"
        />
      </div>
      <div class="commands-list">
        <div
          v-for="command in filteredCommands"
          :key="command.id"
          class="command-item"
          @click="executeCommand(command)"
        >
          <div class="command-content">
            <div class="command-name">{{ command.name }}</div>
            <div class="command-description">{{ command.description }}</div>
          </div>
          <div class="command-shortcut" v-if="command.shortcut">
            {{ command.shortcut }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommandPalette',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'command-executed'],
  data() {
    return {
      searchQuery: '',
      filteredCommands: [],
      commands: [
        { id: 'open-file', name: 'File: Open File', description: 'Open a file in the editor', shortcut: 'Ctrl+O' },
        { id: 'new-file', name: 'File: New File', description: 'Create a new file', shortcut: 'Ctrl+N' },
        { id: 'save-file', name: 'File: Save', description: 'Save the current file', shortcut: 'Ctrl+S' },
        { id: 'close-file', name: 'File: Close', description: 'Close the current file', shortcut: 'Ctrl+W' },
        { id: 'toggle-sidebar', name: 'View: Toggle Sidebar', description: 'Show or hide the sidebar' },
        { id: 'command-palette', name: 'Show Command Palette', description: 'Open command palette', shortcut: 'Ctrl+Shift+P' },
        { id: 'settings', name: 'Preferences: Open Settings', description: 'Open user settings' },
        { id: 'reload-window', name: 'Developer: Reload Window', description: 'Reload the application' }
      ]
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.$refs.searchInput.focus()
          this.filteredCommands = this.commands
        })
      } else {
        this.searchQuery = ''
      }
    }
  },
  methods: {
    filterCommands() {
      if (!this.searchQuery) {
        this.filteredCommands = this.commands
      } else {
        const query = this.searchQuery.toLowerCase()
        this.filteredCommands = this.commands.filter(command =>
          command.name.toLowerCase().includes(query) ||
          command.description.toLowerCase().includes(query)
        )
      }
    },
    handleKeydown(event) {
      if (event.key === 'Escape') {
        this.close()
      } else if (event.key === 'Enter' && this.filteredCommands.length > 0) {
        this.executeCommand(this.filteredCommands[0])
      } else if (event.key === 'ArrowDown') {
        event.preventDefault()
        // Could implement arrow navigation
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        // Could implement arrow navigation
      }
    },
    executeCommand(command) {
      this.$emit('command-executed', command)
      this.close()
    },
    close() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.command-palette-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 100px;
  z-index: 1000;
}

.command-palette {
  width: 600px;
  max-height: 400px;
  background-color: #252526;
  border: 1px solid #3e3e42;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.search-input {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #3e3e42;
}

.search-input i {
  color: #cccccc;
  margin-right: 8px;
}

.search-input input {
  flex: 1;
  background: transparent;
  border: none;
  color: #cccccc;
  font-size: 14px;
  outline: none;
}

.commands-list {
  max-height: 348px;
  overflow-y: auto;
}

.command-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  cursor: pointer;
  border-bottom: 1px solid #3e3e42;
}

.command-item:hover {
  background-color: #37373d;
}

.command-item:last-child {
  border-bottom: none;
}

.command-content {
  flex: 1;
}

.command-name {
  color: #cccccc;
  font-size: 14px;
  margin-bottom: 2px;
}

.command-description {
  color: #888;
  font-size: 12px;
}

.command-shortcut {
  color: #888;
  font-size: 12px;
  font-family: monospace;
}
</style>
