<template>
  <div class="home-view">
    <h2>欢迎使用 Geoflow</h2>
    <p>这是一个地质可视化应用</p>
    <!-- Main application content goes here -->
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
  text-align: center;
}

.home-view h2 {
  font-size: 28px;
  margin-bottom: 16px;
}

.home-view p {
  color: #888;
  font-size: 16px;
}
</style>

