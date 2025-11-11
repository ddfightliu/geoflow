<template>
  <div v-if="show" class="settings-overlay" @click="close">
    <div class="settings-dialog" @click.stop>
      <div class="dialog-header">
        <h3>Settings</h3>
        <button @click="close" class="close-button">×</button>
      </div>
      <div class="dialog-content">
        <div class="settings-section">
          <h4>Appearance</h4>
          <div class="setting-item">
            <label for="theme-select">Theme:</label>
            <select id="theme-select" v-model="selectedTheme" @change="changeTheme">
              <option value="vs-dark">Dark</option>
              <option value="vs">Light</option>
              <option value="hc-black">High Contrast Dark</option>
            </select>
          </div>
        </div>
        <div class="settings-section">
          <h4>Editor</h4>
          <div class="setting-item">
            <label for="font-size">Font Size:</label>
            <input
              id="font-size"
              type="number"
              v-model.number="fontSize"
              @input="changeFontSize"
              min="10"
              max="24"
            />
          </div>
          <div class="setting-item">
            <label for="word-wrap">Word Wrap:</label>
            <input
              id="word-wrap"
              type="checkbox"
              v-model="wordWrap"
              @change="changeWordWrap"
            />
          </div>
        </div>
        <div class="settings-section">
          <h4>Workspace</h4>
          <div class="setting-item">
            <label for="auto-save">Auto Save:</label>
            <select id="auto-save" v-model="autoSave" @change="changeAutoSave">
              <option value="off">Off</option>
              <option value="afterDelay">After Delay</option>
              <option value="onFocusChange">On Focus Change</option>
            </select>
          </div>
        </div>
      </div>
      <div class="dialog-footer">
        <button @click="saveSettings" class="save-button">Save</button>
        <button @click="resetSettings" class="reset-button">Reset</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SettingsDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'settings-changed'],
  data() {
    return {
      selectedTheme: 'vs-dark',
      fontSize: 14,
      wordWrap: true,
      autoSave: 'off'
    }
  },
  mounted() {
    this.loadSettings()
  },
  methods: {
    loadSettings() {
      // Load settings from localStorage or API
      const settings = JSON.parse(localStorage.getItem('geoflow-settings') || '{}')
      this.selectedTheme = settings.theme || 'vs-dark'
      this.fontSize = settings.fontSize || 14
      this.wordWrap = settings.wordWrap !== false
      this.autoSave = settings.autoSave || 'off'
    },
    changeTheme() {
      this.$emit('settings-changed', { theme: this.selectedTheme })
    },
    changeFontSize() {
      this.$emit('settings-changed', { fontSize: this.fontSize })
    },
    changeWordWrap() {
      this.$emit('settings-changed', { wordWrap: this.wordWrap })
    },
    changeAutoSave() {
      this.$emit('settings-changed', { autoSave: this.autoSave })
    },
    saveSettings() {
      const settings = {
        theme: this.selectedTheme,
        fontSize: this.fontSize,
        wordWrap: this.wordWrap,
        autoSave: this.autoSave
      }
      localStorage.setItem('geoflow-settings', JSON.stringify(settings))
      this.$emit('settings-changed', settings)
      this.close()
    },
    resetSettings() {
      localStorage.removeItem('geoflow-settings')
      this.loadSettings()
      this.$emit('settings-changed', {
        theme: 'vs-dark',
        fontSize: 14,
        wordWrap: true,
        autoSave: 'off'
      })
    },
    close() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.settings-dialog {
  width: 500px;
  max-height: 80vh;
  background-color: #252526;
  border: 1px solid #3e3e42;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #3e3e42;
  color: #cccccc;
}

.close-button {
  background: none;
  border: none;
  color: #cccccc;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background-color: #37373d;
  border-radius: 3px;
}

.dialog-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.settings-section {
  margin-bottom: 24px;
}

.settings-section h4 {
  color: #cccccc;
  margin: 0 0 12px 0;
  border-bottom: 1px solid #3e3e42;
  padding-bottom: 4px;
}

.setting-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.setting-item label {
  color: #cccccc;
  width: 120px;
  margin-right: 12px;
}

.setting-item select,
.setting-item input[type="number"] {
  background-color: #3c3c3c;
  border: 1px solid #3e3e42;
  color: #cccccc;
  padding: 4px 8px;
  border-radius: 3px;
}

.setting-item input[type="checkbox"] {
  margin: 0;
}

.dialog-footer {
  padding: 16px 20px;
  border-top: 1px solid #3e3e42;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.save-button,
.reset-button {
  padding: 8px 16px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
}

.save-button {
  background-color: #007acc;
  color: white;
}

.reset-button {
  background-color: #555;
  color: #cccccc;
}

.save-button:hover {
  background-color: #005a9e;
}

.reset-button:hover {
  background-color: #666;
}
</style>
