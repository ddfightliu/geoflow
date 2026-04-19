<template>
    <div class="login-box">
      <!-- Right side - Login Form -->
      <div class="login-form-section">
        <div class="form-header">
          <h2>登录</h2>
          <p class="form-subtitle">使用您的账户继续</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Username input -->
          <div class="input-group">
            <label for="username">用户名</label>
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="请输入用户名或邮箱"
                :disabled="loading"
              />
            </div>
          </div>

          <!-- Password input -->
          <div class="input-group">
            <label for="password">密码</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                :disabled="loading"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>

          <!-- Remember me & Forgot password -->
          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" v-model="rememberMe" />
              <span>记住我</span>
            </label>
            <button type="button" class="forgot-link" @click="showForgotModal = true">忘记密码?</button>
          </div>

          <!-- Forgot Password Modal -->
          <div v-if="showForgotModal" class="modal-overlay" @click="showForgotModal = false">
            <div class="modal" @click.stop>
              <h3>重置密码</h3>
              <form @submit.prevent="handleForgotPassword">
                <div class="input-group">
                  <label for="forgot-email">邮箱地址</label>
                  <input
                    id="forgot-email"
                    v-model="forgotEmail"
                    type="email"
                    placeholder="your@email.com"
                    required
                  />
                </div>
                <div class="modal-actions">
                  <button type="button" @click="showForgotModal = false" class="cancel-btn">取消</button>
                  <button type="submit" class="confirm-btn" :disabled="!forgotEmail">发送重置链接</button>
                </div>
              </form>
            </div>
          </div>

          <!-- Error message -->
          <div v-if="error" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ error }}
          </div>

          <!-- Login button -->
          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else>登录</span>
          </button>
        </form>

        <!-- Divider -->
        <div class="divider">
          <span>或</span>
        </div>

        <!-- Social login buttons -->
        <div class="social-login">
          <button
            v-for="provider in availableProviders"
            :key="provider.id"
            class="social-btn"
            :disabled="!provider.enabled || loading"
            @click="handleSocialLogin(provider.id)"
          >
            <i :class="getProviderIcon(provider.id)"></i>
            <span>使用 {{ provider.name }} 登录</span>
          </button>
        </div>

        <!-- Register link -->
        <div class="register-section">
          <p>
            还没有账户?
            <router-link to="/register" class="register-link">立即注册</router-link>
          </p>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { loading, error, availableProviders } = storeToRefs(authStore)

const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const showForgotModal = ref(false)
const forgotEmail = ref('')

const handleLogin = () => {
  if (!username.value || !password.value) return
  authStore.loginWithCredentials({
    username: username.value,
    password: password.value,
    remember_me: rememberMe.value
  })
}

const handleForgotPassword = async () => {
  if (!forgotEmail.value) return
  try {
    await authStore.forgotPassword(forgotEmail.value)
    alert('重置链接已发送，请检查邮箱 (demo模式)')
    showForgotModal.value = false
  } catch (err) {
    console.error('Forgot password error:', err)
  }
}

const handleSocialLogin = (providerId) => {
  authStore.loginWithProvider(providerId)
}

const getProviderIcon = (providerId) => {
  const icons = {
    github: 'fab fa-github',
    google: 'fab fa-google',
    microsoft: 'fab fa-microsoft',
    qq: 'fab fa-qq',
    wechat: 'fab fa-weixin'
  }
  return icons[providerId] || 'fas fa-sign-in-alt'
}

const checkOAuthCallback = () => {
  let token = null
  let userId = null
  
  const urlParams = new URLSearchParams(window.location.search)
  token = urlParams.get('token')
  userId = urlParams.get('user_id')
  
  if (!token && window.location.hash) {
    const hashParams = new URLSearchParams(window.location.hash.substring(1))
    token = hashParams.get('token')
    userId = hashParams.get('user_id')
  }
  
  if (token && userId) {
    authStore.setToken(token)
    const cleanHash = window.location.hash.split('?')[0]
    window.history.replaceState({}, document.title, cleanHash || '/#/login/success')
    router.push('/')
  }
}

onMounted(() => {
  console.log('欢迎来到登录页面! 👋')
  authStore.clearError()
  authStore.fetchProviders()
  checkOAuthCallback()
})
</script>

<style scoped>

.login-box {
  display: flex;
  width: 800px;
  max-width: 100%;
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.login-branding {
  flex: 1;
  background: linear-gradient(135deg, #ff2a6d 0%, #8338ec 50%, #05d9e8 100%);
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.login-branding::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.3;
}

.branding-content {
  position: relative;
  z-index: 1;
}

.brand-title {
  font-size: 42px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 16px 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.brand-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.login-form-section {
  flex: 1;
  padding: 40px;
  background: #252526;
}

.form-header {
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #cccccc;
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 14px;
  color: #808080;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 14px;
  font-weight: 500;
  color: #cccccc;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: #808080;
  font-size: 14px;
}

.input-wrapper input {
  width: 100%;
  padding: 10px 12px 10px 38px;
  background: #3c3c3c;
  border: 1px solid #3c3c3c;
  border-radius: 4px;
  color: #cccccc;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper input:focus {
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
  outline: none;
}

.input-wrapper input::placeholder {
  color: #6e6e6e;
}

.input-wrapper input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.password-toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #808080;
  cursor: pointer;
  padding: 4px;
}

.password-toggle:hover {
  color: #cccccc;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #cccccc;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #007acc;
}

.forgot-link {
  font-size: 14px;
  color: #0078d4;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(247, 82, 73, 0.1);
  border: 1px solid rgba(247, 82, 73, 0.3);
  border-radius: 4px;
  color: #f75249;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  padding: 10px 16px;
  background: #0078d4;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-btn:hover:not(:disabled) {
  background: #106ebe;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: #808080;
  font-size: 12px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #3c3c3c;
}

.divider span {
  padding: 0 16px;
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.social-btn {
  width: 100%;
  padding: 10px 16px;
  background: #3c3c3c;
  border: 1px solid #3c3c3c;
  border-radius: 4px;
  color: #cccccc;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: background-color 0.2s, border-color 0.2s;
}

.social-btn:hover:not(:disabled) {
  background: #4a4a4a;
  border-color: #5a5a5a;
}

.social-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.social-btn i {
  font-size: 18px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.modal {
  background: #252526;
  padding: 40px;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.modal h3 {
  margin: 0 0 24px 0;
  font-size: 24px;
  color: #e0e0e0;
  text-align: center;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn, .confirm-btn {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.cancel-btn {
  background: #404040;
  color: #e0e0e0;
}

.confirm-btn {
  background: #0078d4;
  color: white;
}

.confirm-btn:disabled {
  opacity: 0.6;
}

.register-section {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #808080;
}

.register-link {
  color: #0078d4;
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .login-box {
    flex-direction: column;
  }

  .login-branding {
    padding: 30px;
  }

  .brand-title {
    font-size: 32px;
  }

  .login-form-section {
    padding: 30px;
  }
}
</style>
