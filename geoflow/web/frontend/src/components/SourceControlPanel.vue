<template>
  <div class="source-control-panel">
    <div class="panel-header">
      <h3>Source Control</h3>
    </div>
    <div class="git-status">
      <div v-if="gitStatus.changes.length === 0" class="no-changes">
        No changes
      </div>
      <div v-else>
        <div class="changes-summary">
          {{ gitStatus.changes.length }} changes
        </div>
        <div class="changes-list">
          <div
            v-for="change in gitStatus.changes"
            :key="change.file"
            class="change-item"
          >
            <span class="change-type" :class="change.type">{{ change.type }}</span>
            <span class="change-file">{{ change.file }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="commit-section">
      <textarea
        v-model="commitMessage"
        placeholder="Commit message..."
        rows="3"
      ></textarea>
      <button @click="commitChanges" :disabled="!commitMessage.trim() || gitStatus.changes.length === 0">
        Commit
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SourceControlPanel',
  data() {
    return {
      gitStatus: { changes: [] },
      commitMessage: ''
    }
  },
  mounted() {
    this.loadGitStatus()
  },
  methods: {
    async loadGitStatus() {
      try {
        const response = await fetch('/api/git-status')
        const data = await response.json()
        this.gitStatus = data
      } catch (error) {
        console.error('Failed to load git status:', error)
      }
    },
    async commitChanges() {
      try {
        const response = await fetch('/api/git-commit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: this.commitMessage })
        })
        if (response.ok) {
          this.commitMessage = ''
          this.loadGitStatus()
          alert('Changes committed successfully')
        } else {
          alert('Failed to commit changes')
        }
      } catch (error) {
        console.error('Commit failed:', error)
        alert('Error committing changes')
      }
    }
  }
}
</script>

<style scoped>
.source-control-panel {
  width: 100%;
  height: 100%;
  background-color: #252526;
  color: #cccccc;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 10px;
  border-bottom: 1px solid #3e3e42;
}

.git-status {
  flex: 1;
  padding: 10px;
}

.no-changes {
  text-align: center;
  color: #888;
  margin-top: 20px;
}

.changes-summary {
  font-weight: bold;
  margin-bottom: 10px;
}

.changes-list {
  margin-bottom: 20px;
}

.change-item {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.change-type {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  margin-right: 8px;
}

.change-type.M {
  background-color: #007acc;
  color: white;
}

.change-type.A {
  background-color: #388a34;
  color: white;
}

.change-type.D {
  background-color: #f48771;
  color: white;
}

.change-file {
  font-family: monospace;
  font-size: 14px;
}

.commit-section {
  padding: 10px;
  border-top: 1px solid #3e3e42;
}

.commit-section textarea {
  width: 100%;
  background-color: #3c3c3c;
  border: 1px solid #3e3e42;
  color: #cccccc;
  padding: 8px;
  border-radius: 3px;
  margin-bottom: 10px;
  resize: vertical;
}

.commit-section button {
  width: 100%;
  padding: 8px;
  background-color: #007acc;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.commit-section button:disabled {
  background-color: #555;
  cursor: not-allowed;
}
</style>
