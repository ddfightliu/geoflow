<template>
  <div style="width: 250px; background-color: #252526; border-right: 1px solid #3e3e42; padding: 10px;">
    <h3 style="color: #cccccc; margin: 0 0 10px 0;">Project</h3>
    <div v-if="projectData">
      <div style="color: #cccccc; margin-bottom: 10px;">
        {{ projectData.name }}
      </div>
      <div>
        <div
          v-for="file in projectData.files"
          :key="file"
          style="color: #cccccc; padding: 4px 8px; cursor: pointer; border-radius: 3px;"
          @click="$emit('file-open', file)"
        >
          📄 {{ file }}
        </div>
      </div>
    </div>
    <div v-else style="color: #888;">
      Loading project...
    </div>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    projectData: {
      type: Object,
      default: null
    }
  },
  emits: ['file-open']
}
</script>

<style scoped>
/* Add any scoped styles here if needed */
</style>
