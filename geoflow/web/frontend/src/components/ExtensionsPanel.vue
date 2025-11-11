<template>
  <div class="extensions-panel">
    <div class="panel-header">
      <h3>Extensions</h3>
    </div>
    <div class="extensions-content">
      <div class="placeholder">
        <i class="fas fa-puzzle-piece"></i>
        <p>Extensions panel coming soon...</p>
        <p>This will allow installing and managing extensions for Geoflow.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExtensionsPanel'
}
</script>

<style scoped>
.extensions-panel {
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

.extensions-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.placeholder {
  text-align: center;
  color: #888;
}

.placeholder i {
  font-size: 48px;
  margin-bottom: 20px;
  display: block;
}

.placeholder p {
  margin: 10px 0;
}
</style>
