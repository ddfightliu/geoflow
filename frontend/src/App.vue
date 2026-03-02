<template>
  <div id="app" class="app-container">
    <div v-if="isAuthenticated" class="app-header">
      <div class="header-left">
        <h1>Geoflow</h1>
      </div>
      <div class="header-right">
        <span v-if="currentUser" class="user-info">
          <img v-if="currentUser.avatar_url" :src="currentUser.avatar_url" alt="Avatar" class="user-avatar">
          <span class="user-name">{{ currentUser.username }}</span>
        </span>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </div>
    </div>
    
    <div class="app-content">
      <router-view v-if="isAuthenticated" />
      <Login v-else />
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'pinia'
import { useAuthStore } from './stores/auth'
import Login from './views/Login.vue'

export default {
  name: 'App',
  components: {
    Login
  },
  computed: {
    ...mapState(useAuthStore, ['isAuthenticated', 'currentUser', 'token'])
  },
  methods: {
    ...mapActions(useAuthStore, ['logout', 'fetchCurrentUser']),
    
    handleLogout() {
      this.logout()
      this.$router.push('/login')
    }
  },
  created() {
    if (this.token) {
      this.fetchCurrentUser()
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
  background: #1e1e1e;
  color: #fff;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #2d2d2d;
  border-bottom: 1px solid #3d3d3d;
}

.header-left h1 {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.user-name {
  color: #ccc;
  font-size: 14px;
}

.logout-btn {
  padding: 8px 16px;
  background: #4a4a4a;
  border: none;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  background: #5a5a5a;
}

.app-content {
  height: calc(100vh - 65px);
}
</style>
