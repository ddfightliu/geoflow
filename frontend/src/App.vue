<template>
  <div id="app" class="app-container">
    <!-- VSCode-style title bar -->
    <div class="title-bar" v-if="isAuthenticated">
      <div class="title-bar-left">
        <span class="app-icon">⚡</span>
        <span class="app-title">虚拟点交易平台 - {{ currentViewTitle }}</span>
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
          <span>虚拟点钱包</span>
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
        <LoginComponent v-else />
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

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { storeToRefs } from 'pinia'
import LoginComponent from './views/Login.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { isAuthenticated, token } = storeToRefs(authStore)

const currentActivity = ref('explorer')
const showEditorTabs = ref(false)
const sections = reactive({
  files: true,
  search: false,
  git: false
})

const activityItems = [
  { id: 'explorer', icon: 'fas fa-file-alt', title: '资源管理器' },
  { id: 'search', icon: 'fas fa-search', title: '搜索' },
  { id: 'git', icon: 'fas fa-code-branch', title: '源代码管理' },
  { id: 'debug', icon: 'fas fa-bug', title: '调试' },
  { id: 'extensions', icon: 'fas fa-th-large', title: '扩展' }
]

const currentViewTitle = computed(() => {
  const routeName = route.name || 'Home'
  return routeName
})

const currentFilePath = computed(() => 'src > views > Home.vue')

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const toggleSection = (section) => {
  sections[section] = !sections[section]
}

const minimizeWindow = () => {
  console.log('Minimize window')
}

const maximizeWindow = () => {
  console.log('Maximize window')
}

const closeWindow = () => {
  if (confirm('确定要退出吗?')) {
    handleLogout()
    window.close()
  }
}

onMounted(() => {
  console.log('GeoFlow App loaded! 🚀')
  if (token.value) {
    authStore.fetchCurrentUser()
  }
})
</script>

<style>
/* Global styles from style.css already applied */
</style>

<style scoped>
/* All existing scoped styles preserved */
.app-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  color: #cccccc;
  overflow: hidden;
}

/* ... rest of existing styles unchanged ... */
</style>
