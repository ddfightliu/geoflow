<template>
  <div id="app" class="app-container">
    <!-- VSCode-style title bar -->
    <div class="title-bar" v-if="isAuthenticated">
      <div class="title-bar-left">
        <span class="app-icon">🌍</span>
        <span class="app-title">Geoflow - {{ currentViewTitle }}</span>
      </div>
      <div class="title-bar-center">
        <span class="file-path">{{ currentFilePath }}</span>
      </div>
      <div class="title-bar-right">
        <button class="title-btn" @click="minimizeWindow" title="最小化">
          <i class="fas fa-minus"></i>
        </button>
        <button class="title-btn" @click="maximizeWindow" title="最大化">
          <i class="fas fa-square"></i>
        </button>
        <button class="title-btn close-btn" @click="closeWindow" title="关闭">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- Main layout -->
    <div class="main-layout">
      <!-- Sidebar (Activity Bar) -->
      <div class="activity-bar" v-if="isAuthenticated">
        <div class="activity-icons">
          <button 
            v-for="item in activityItems" 
            :key="item.id"
            class="activity-btn"
            :class="{ active: currentActivity === item.id }"
            :title="item.title"
            @click="currentActivity = item.id"
          >
            <i :class="item.icon"></i>
          </button>
        </div>
        <div class="activity-bottom">
          <button class="activity-btn" title="设置">
            <i class="fas fa-cog"></i>
          </button>
          <button class="activity-btn" @click="handleLogout" title="账户">
            <i class="fas fa-user-circle"></i>
          </button>
        </div>
      </div>

      <!-- Sidebar (Explorer) -->
      <div class="sidebar" v-if="isAuthenticated">
        <div class="sidebar-header">
          <span>资源管理器</span>
        </div>
        <div class="sidebar-content">
          <div class="sidebar-section">
            <div class="section-header" @click="toggleSection('files')">
              <i :class="sections.files ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i>
              <span>项目文件</span>
            </div>
            <div v-if="sections.files" class="section-content">
              <div class="file-tree">
                <div class="file-item">
                  <i class="fas fa-folder-open"></i>
                  <span>geoflow</span>
                </div>
                <div class="file-item indent">
                  <i class="fas fa-file-code"></i>
                  <span>main.py</span>
                </div>
                <div class="file-item indent">
                  <i class="fas fa-file-alt"></i>
                  <span>config.json</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content area -->
      <div class="content-area">
        <!-- Authenticated: Show router view -->
        <template v-if="isAuthenticated">
          <div class="editor-tabs" v-if="showEditorTabs">
            <div class="editor-tab active">
              <i class="fas fa-file-code"></i>
              <span>Home.vue</span>
              <button class="tab-close"><i class="fas fa-times"></i></button>
            </div>
          </div>
          <div class="editor-content">
            <router-view />
          </div>
        </template>
        
        <!-- Not authenticated: Show Login -->
        <Login v-else />
      </div>
    </div>

    <!-- Status bar -->
    <div class="status-bar" v-if="isAuthenticated">
      <div class="status-left">
        <span class="status-item">
          <i class="fas fa-code-branch"></i> main
        </span>
        <span class="status-item">
          <i class="fas fa-sync-alt"></i> 0↓ 0↑
        </span>
      </div>
      <div class="status-right">
        <span class="status-item synthwave-indicator">
          <i class="fas fa-moon"></i> Synthwave
        </span>
        <span class="status-item">
          <i class="fas fa-code"></i> UTF-8
        </span>
        <span class="status-item">
          <i class="fas fa-bell"></i>
        </span>
      </div>
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
  data() {
    return {
      currentActivity: 'explorer',
      showEditorTabs: false,
      sections: {
        files: true,
        search: false,
        git: false
      },
      activityItems: [
        { id: 'explorer', icon: 'fas fa-file-alt', title: '资源管理器' },
        { id: 'search', icon: 'fas fa-search', title: '搜索' },
        { id: 'git', icon: 'fas fa-code-branch', title: '源代码管理' },
        { id: 'debug', icon: 'fas fa-bug', title: '调试' },
        { id: 'extensions', icon: 'fas fa-th-large', title: '扩展' }
      ]
    }
  },
  computed: {
    ...mapState(useAuthStore, ['isAuthenticated', 'currentUser', 'token']),
    currentViewTitle() {
      const routeName = this.$route.name || 'Home'
      return routeName
    },
    currentFilePath() {
      return 'src > views > Home.vue'
    }
  },
  methods: {
    ...mapActions(useAuthStore, ['logout', 'fetchCurrentUser']),
    
    handleLogout() {
      this.logout()
      this.$router.push('/login')
    },
    
    toggleSection(section) {
      this.sections[section] = !this.sections[section]
    },
    
    minimizeWindow() {
      // For web, this would typically minimize the browser window
      // In Electron, this would call window.minimize()
      console.log('Minimize window')
    },
    
    maximizeWindow() {
      console.log('Maximize window')
    },
    
    closeWindow() {
      if (confirm('确定要退出吗?')) {
        this.handleLogout()
        window.close()
      }
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
/* Global styles from style.css are already applied */
</style>

<style scoped>
.app-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  color: #cccccc;
  overflow: hidden;
}

/* Title Bar */
.title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 30px;
  background: #333333;
  padding: 0 8px;
  -webkit-app-region: drag;
  user-select: none;
}

.title-bar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-icon {
  font-size: 14px;
}

.app-title {
  font-size: 12px;
  color: #cccccc;
}

.title-bar-center {
  flex: 1;
  text-align: center;
}

.file-path {
  font-size: 12px;
  color: #858585;
}

.title-bar-right {
  display: flex;
  -webkit-app-region: no-drag;
}

.title-btn {
  width: 46px;
  height: 30px;
  background: transparent;
  border: none;
  color: #cccccc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.1s;
}

.title-btn:hover {
  background: #505050;
}

.close-btn:hover {
  background: #e81123;
  color: #ffffff;
}

/* Main Layout */
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Activity Bar */
.activity-bar {
  width: 50px;
  background: #333333;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 8px 0;
}

.activity-icons,
.activity-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.activity-btn {
  width: 50px;
  height: 50px;
  background: transparent;
  border: none;
  color: #858585;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: color 0.1s;
}

.activity-btn:hover {
  color: #cccccc;
}

.activity-btn.active {
  color: #ffffff;
  border-left: 2px solid #007acc;
}

/* Sidebar */
.sidebar {
  width: 250px;
  background: #252526;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 10px 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #bbbbbb;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 4px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #bbbbbb;
}

.section-header:hover {
  background: #2a2d2e;
}

.section-header i {
  font-size: 10px;
  width: 16px;
}

.section-content {
  padding-left: 12px;
}

.file-tree {
  padding: 4px 0;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #cccccc;
}

.file-item:hover {
  background: #2a2d2e;
}

.file-item i {
  color: #858585;
  font-size: 12px;
}

.file-item.indent {
  padding-left: 28px;
}

/* Content Area */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  overflow: hidden;
}

/* Editor Tabs */
.editor-tabs {
  display: flex;
  background: #2d2d30;
  height: 35px;
}

.editor-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 12px;
  background: #2d2d30;
  color: #969696;
  font-size: 13px;
  cursor: pointer;
  border-right: 1px solid #252526;
}

.editor-tab.active {
  background: #1e1e1e;
  color: #ffffff;
}

.editor-tab i {
  font-size: 12px;
}

.tab-close {
  background: none;
  border: none;
  color: #969696;
  cursor: pointer;
  padding: 2px 4px;
  margin-left: 4px;
}

.tab-close:hover {
  color: #cccccc;
}

/* Editor Content */
.editor-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

/* Status Bar */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 22px;
  background: #007acc;
  padding: 0 8px;
  font-size: 12px;
  color: #ffffff;
}

.status-left,
.status-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.status-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.synthwave-indicator {
  background: linear-gradient(90deg, #ff2a6d, #8338ec, #05d9e8);
  padding: 2px 8px;
  border-radius: 2px;
}

/* Responsive */
@media (max-width: 768px) {
  .activity-bar,
  .sidebar {
    display: none;
  }
  
  .title-bar-center {
    display: none;
  }
}
</style>

