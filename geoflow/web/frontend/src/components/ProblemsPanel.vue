<template>
  <div class="problems-panel">
    <div class="panel-header">
      <h3>Problems</h3>
    </div>
    <div class="problems-content">
      <div v-if="problems.length === 0" class="no-problems">
        <i class="fas fa-check-circle"></i>
        <p>No problems found</p>
      </div>
      <div v-else>
        <div class="problems-summary">
          {{ problems.length }} problems
        </div>
        <div class="problems-list">
          <div
            v-for="problem in problems"
            :key="problem.id"
            class="problem-item"
            @click="openFile(problem)"
          >
            <span class="problem-type" :class="problem.severity">{{ problem.severity }}</span>
            <div class="problem-details">
              <div class="problem-message">{{ problem.message }}</div>
              <div class="problem-location">{{ problem.file }}:{{ problem.line }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProblemsPanel',
  data() {
    return {
      problems: []
    }
  },
  mounted() {
    this.loadProblems()
  },
  methods: {
    async loadProblems() {
      try {
        const response = await fetch('/api/problems')
        const data = await response.json()
        this.problems = data.problems || []
      } catch (error) {
        console.error('Failed to load problems:', error)
      }
    },
    openFile(problem) {
      this.$emit('file-open', problem.file)
    }
  }
}
</script>

<style scoped>
.problems-panel {
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

.problems-content {
  flex: 1;
  padding: 10px;
}

.no-problems {
  text-align: center;
  color: #888;
  margin-top: 40px;
}

.no-problems i {
  font-size: 48px;
  color: #388a34;
  margin-bottom: 20px;
  display: block;
}

.problems-summary {
  font-weight: bold;
  margin-bottom: 10px;
}

.problems-list {
  overflow-y: auto;
}

.problem-item {
  display: flex;
  align-items: flex-start;
  padding: 8px;
  border-bottom: 1px solid #3e3e42;
  cursor: pointer;
  border-radius: 3px;
}

.problem-item:hover {
  background-color: #37373d;
}

.problem-type {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  margin-right: 8px;
  margin-top: 2px;
}

.problem-type.error {
  background-color: #f48771;
  color: white;
}

.problem-type.warning {
  background-color: #cca700;
  color: white;
}

.problem-type.info {
  background-color: #3794ff;
  color: white;
}

.problem-details {
  flex: 1;
}

.problem-message {
  font-size: 14px;
  margin-bottom: 4px;
}

.problem-location {
  font-family: monospace;
  font-size: 12px;
  color: #888;
}
</style>
