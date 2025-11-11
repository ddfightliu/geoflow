<template>
  <div style="height: 100%; display: flex; flex-direction: column;">
    <div style="padding: 10px; background-color: #007acc; color: white; display: flex; justify-content: space-between; align-items: center;">
      <span>{{ fileName }}</span>
      <button
        @click="handleSave"
        style="background-color: #005a9e; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;"
      >
        Save
      </button>
    </div>
    <div ref="editorContainer" style="flex: 1;"></div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor'

export default {
  name: 'Editor',
  props: {
    fileName: {
      type: String,
      required: true
    },
    settings: {
      type: Object,
      default: () => ({
        theme: 'vs-dark',
        fontSize: 14,
        wordWrap: true
      })
    }
  },
  data() {
    return {
      editor: null,
      loading: true
    }
  },
  mounted() {
    this.initEditor()
    this.loadFileContent()
  },
  beforeUnmount() {
    if (this.editor) {
      this.editor.dispose()
    }
  },
  watch: {
    fileName: {
      immediate: true,
      handler() {
        this.loadFileContent()
      }
    }
  },
  methods: {
    initEditor() {
      this.editor = monaco.editor.create(this.$refs.editorContainer, {
        value: '',
        language: this.getLanguageFromFileName(this.fileName),
        theme: this.settings.theme,
        fontSize: this.settings.fontSize,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        wordWrap: this.settings.wordWrap ? 'on' : 'off'
      })
    },
    getLanguageFromFileName(fileName) {
      const ext = fileName.split('.').pop().toLowerCase()
      const langMap = {
        'py': 'python',
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'json': 'json',
        'md': 'markdown',
        'html': 'html',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'less': 'less',
        'xml': 'xml',
        'yaml': 'yaml',
        'yml': 'yaml',
        'sh': 'shell',
        'bash': 'shell',
        'zsh': 'shell',
        'sql': 'sql',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'h': 'c',
        'hpp': 'cpp',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'dart': 'dart',
        'lua': 'lua',
        'perl': 'perl',
        'r': 'r',
        'matlab': 'matlab'
      }
      return langMap[ext] || 'plaintext'
    },
    async loadFileContent() {
      this.loading = true
      try {
        const response = await fetch(`/api/files/${encodeURIComponent(this.fileName)}`)
        if (response.ok) {
          const data = await response.json()
          if (this.editor) {
            this.editor.setValue(data.content)
          }
        } else {
          if (this.editor) {
            this.editor.setValue('File not found')
          }
        }
      } catch (error) {
        console.error('Failed to load file:', error)
        if (this.editor) {
          this.editor.setValue('Error loading file')
        }
      } finally {
        this.loading = false
      }
    },
    async handleSave() {
      if (!this.editor) return
      try {
        const content = this.editor.getValue()
        const response = await fetch(`/api/files/${encodeURIComponent(this.fileName)}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ content })
        })
        if (response.ok) {
          alert('File saved successfully')
        } else {
          alert('Failed to save file')
        }
      } catch (error) {
        console.error('Failed to save file:', error)
        alert('Error saving file')
      }
    }
  }
}
</script>

<style scoped>
/* Add any scoped styles here if needed */
</style>
