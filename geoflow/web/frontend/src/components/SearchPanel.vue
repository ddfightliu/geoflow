<template>
  <div class="search-panel">
    <div class="search-header">
      <h3>Search</h3>
    </div>
    <div class="search-input">
      <input
        v-model="searchQuery"
        @input="performSearch"
        placeholder="Search files and content..."
        type="text"
      />
    </div>
    <div class="search-results">
      <div v-if="searchResults.length === 0 && searchQuery" class="no-results">
        No results found
      </div>
      <div
        v-for="result in searchResults"
        :key="result.file + result.line"
        class="search-result"
        @click="openFile(result)"
      >
        <div class="result-file">{{ result.file }}</div>
        <div class="result-line">{{ result.line }}: {{ result.content }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchPanel',
  data() {
    return {
      searchQuery: '',
      searchResults: []
    }
  },
  methods: {
    async performSearch() {
      if (!this.searchQuery.trim()) {
        this.searchResults = []
        return
      }
      try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(this.searchQuery)}`)
        const data = await response.json()
        this.searchResults = data.results || []
      } catch (error) {
        console.error('Search failed:', error)
        this.searchResults = []
      }
    },
    openFile(result) {
      this.$emit('file-open', result.file)
    }
  }
}
</script>

<style scoped>
.search-panel {
  width: 100%;
  height: 100%;
  background-color: #252526;
  color: #cccccc;
  display: flex;
  flex-direction: column;
}

.search-header {
  padding: 10px;
  border-bottom: 1px solid #3e3e42;
}

.search-input {
  padding: 10px;
}

.search-input input {
  width: 100%;
  padding: 8px;
  background-color: #3c3c3c;
  border: 1px solid #3e3e42;
  color: #cccccc;
  border-radius: 3px;
}

.search-results {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.no-results {
  text-align: center;
  color: #888;
  margin-top: 20px;
}

.search-result {
  padding: 8px;
  border-bottom: 1px solid #3e3e42;
  cursor: pointer;
  border-radius: 3px;
}

.search-result:hover {
  background-color: #37373d;
}

.result-file {
  font-weight: bold;
  color: #007acc;
}

.result-line {
  font-family: monospace;
  font-size: 12px;
  margin-top: 4px;
}
</style>
