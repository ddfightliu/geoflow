<template>
  <div style="padding: 20px;">
    <h1 style="color: #ffffff;">Welcome to Geoflow Web</h1>
    <p style="color: #cccccc;">Choose a view to get started:</p>
    <div style="display: flex; gap: 20px; margin-top: 20px;">
      <div
        v-for="view in views"
        :key="view.type"
        style="background-color: #252526; border: 1px solid #3e3e42; border-radius: 8px; padding: 20px; cursor: pointer; min-width: 200px; text-align: center;"
        @click="handleViewClick(view)"
      >
        <h3 style="color: #ffffff; margin: 0 0 10px 0;">{{ view.name }}</h3>
        <p style="color: #cccccc; margin: 0;">Click to open {{ view.name.toLowerCase() }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Views',
  data() {
    return {
      views: []
    }
  },
  mounted() {
    this.loadViews()
  },
  methods: {
    async loadViews() {
      try {
        const response = await fetch('/api/views')
        const data = await response.json()
        this.views = data.views
      } catch (error) {
        console.error('Failed to load views:', error)
      }
    },
    handleViewClick(view) {
      alert(`Opening ${view.name}`) // Placeholder action
    }
  }
}
</script>

<style scoped>
/* Add any scoped styles here if needed */
</style>
