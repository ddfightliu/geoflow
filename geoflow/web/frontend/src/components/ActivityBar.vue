<template>
  <div class="activity-bar">
    <div
      v-for="item in activityItems"
      :key="item.id"
      :class="['activity-item', { active: activePanel === item.id }]"
      @click="setActivePanel(item.id)"
      :title="item.title"
    >
      <i :class="item.icon"></i>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActivityBar',
  props: {
    activePanel: {
      type: String,
      default: 'explorer'
    }
  },
  emits: ['panel-change'],
  data() {
    return {
      activityItems: [
        { id: 'explorer', icon: 'fas fa-folder', title: 'Explorer' },
        { id: 'search', icon: 'fas fa-search', title: 'Search' },
        { id: 'source-control', icon: 'fab fa-git-alt', title: 'Source Control' },
        { id: 'extensions', icon: 'fas fa-puzzle-piece', title: 'Extensions' },
        { id: 'problems', icon: 'fas fa-exclamation-triangle', title: 'Problems' },
        { id: 'settings', icon: 'fas fa-cog', title: 'Settings' }
      ]
    }
  },
  methods: {
    setActivePanel(panelId) {
      this.$emit('panel-change', panelId)
    }
  }
}
</script>

<style scoped>
.activity-bar {
  width: 50px;
  background-color: #2d2d30;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
  border-right: 1px solid #3e3e42;
}

.activity-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #cccccc;
  border-radius: 4px;
  margin-bottom: 5px;
  transition: background-color 0.2s;
}

.activity-item:hover {
  background-color: #37373d;
}

.activity-item.active {
  background-color: #007acc;
  color: white;
}

.activity-item i {
  font-size: 18px;
}
</style>
