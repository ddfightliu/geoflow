<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1 class="login-title">Geoflow</h1>
        <p class="login-subtitle">登录到您的账户</p>
      </div>

      <div class="login-providers">
        <LoginButton
          v-for="provider in providers"
          :key="provider.id"
          :provider="provider.id"
          :text="`使用 ${provider.name} 登录`"
          :disabled="!provider.enabled || loading"
          @click="handleLogin"
        />
      </div>

      <div v-if="error" class="login-error">
        {{ error }}
      </div>

      <div class="login-footer">
        <p class="login-note">
          登录即表示您同意我们的服务条款和隐私政策
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'pinia'
import { useAuthStore } from '../stores/auth'
import LoginButton from '../components/LoginButton.vue'

export default {
  name: 'LoginView',
  components: {
    LoginButton
  },
  computed: {
    ...mapState(useAuthStore, ['providers', 'loading', 'error']),
    providers() {
      const authStore = useAuthStore()
      return authStore.availableProviders || []
    }
  },
  methods: {
    ...mapActions(useAuthStore, ['loginWithProvider', 'setToken', 'fetchProviders']),
    
    handleLogin(provider) {
      this.loginWithProvider(provider)
    },
    
    checkOAuthCallback() {
      // Check for OAuth token in URL
      const urlParams = new URLSearchParams(window.location.search)
      const token = urlParams.get('token')
      const userId = urlParams.get('user_id')
      
      if (token && userId) {
        this.setToken(token)
        // Clean URL
        window.history.replaceState({}, document.title, '/#/login')
      }
    }
  },
  created() {
    const authStore = useAuthStore()
    authStore.fetchProviders()
    this.checkOAuthCallback()
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.login-providers {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.login-error {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 59, 48, 0.1);
  border: 1px solid rgba(255, 59, 48, 0.3);
  border-radius: 8px;
  color: #ff3b30;
  font-size: 14px;
  text-align: center;
}

.login-footer {
  margin-top: 32px;
  text-align: center;
}

.login-note {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}
</style>

