<template>
  <div class="register-page">
    <div class="register-box">
      <!-- Branding -->
      <div class="register-branding">
        <div class="branding-content">
          <h1 class="brand-title">虚拟点交易平台</h1>
          <p class="brand-subtitle">加入游戏世界，开启虚拟点交易之旅</p>
          
        </div>
      </div>

      <!-- Register Form -->
      <div class="register-form-section">
        <div class="form-header">
          <h2 v-if="!successMode">注册新账户</h2>
          <h2 v-else class="success-title">注册成功!</h2>
          <p v-if="!successMode" class="form-subtitle">创建账户开始交易虚拟点</p>
          <p v-else class="success-subtitle">{{ successMessage }}</p>
        </div>

        <form @submit.prevent="handleRegister" class="register-form">
          <!-- Username -->
          <div class="input-group">
            <label for="username">用户名</label>
            <div class="input-wrapper">
              <i class="fas fa-user input-icon"></i>
              <input
                id="username"
                v-model="form.username"
                type="text"
                placeholder="选择一个独特的用户名"
                :disabled="loading"
                @input="errors.username = ''"
              />
            </div>
            <div v-if="errors.username" class="field-error">{{ errors.username }}</div>
          </div>

          <!-- Email -->
          <div class="input-group">
            <label for="email">邮箱</label>
            <div class="input-wrapper">
              <i class="fas fa-envelope input-icon"></i>
              <input
                id="email"
                v-model="form.email"
                type="email"
                placeholder="your@email.com"
                :disabled="loading"
                @input="errors.email = ''"
              />
            </div>
            <div v-if="errors.email" class="field-error">{{ errors.email }}</div>
          </div>

          <!-- Password -->
          <div class="input-group">
            <label for="password">密码</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="至少8位字符"
                :disabled="loading"
                @input="validatePassword"
              />
              <button type="button" class="password-toggle" @click="showPassword = !showPassword">
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <div v-if="form.password && !errors.password" class="password-strength" :class="passwordStrengthClass">
              强度: {{ passwordStrengthText }}
            </div>
            <div v-if="errors.password" class="field-error">{{ errors.password }}</div>
          </div>

          <!-- Confirm Password -->
          <div class="input-group">
            <label for="confirmPassword">确认密码</label>
            <div class="input-wrapper">
              <i class="fas fa-lock input-icon"></i>
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="再次输入密码"
                :disabled="loading"
                @input="validateConfirmPassword"
              />
              <button type="button" class="password-toggle" @click="showConfirmPassword = !showConfirmPassword">
                <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <div v-if="errors.confirmPassword" class="field-error">{{ errors.confirmPassword }}</div>
          </div>

          <!-- Global Error message -->
          <div v-if="globalError" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ globalError }}
          </div>

          <!-- Success message -->
          <div v-if="successMode" class="success-message">
            <i class="fas fa-check-circle"></i>
            账户已创建！<br>获得 1000 虚拟点欢迎奖励<br>2秒后自动跳转登录...
          </div>

          <!-- Register button -->
          <button v-if="!successMode" type="submit" class="register-btn" :disabled="loading || !isFormValid">
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else>立即注册</span>
          </button>
        </form>

        <!-- Social register -->
        <div class="divider">
          <span>或使用第三方登录</span>
        </div>

        <div class="social-login">
          <button
            v-for="provider in availableProviders"
            :key="provider.id"
            class="social-btn"
            :disabled="!provider.enabled || loading"
            @click="handleSocialLogin(provider.id)"
          >
            <i :class="getProviderIcon(provider.id)"></i>
            <span>使用 {{ provider.name }} 注册</span>
          </button>
        </div>

        <!-- Login link -->
        <div class="login-section">
          <p>
            已有账户? 
            <router-link to="/login" class="login-link">立即登录</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
console.log('Register.vue loaded') // Debug log to confirm component load
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { loading, error: authError, availableProviders, registerSuccess } = storeToRefs(authStore)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const errors = ref({})
const globalError = ref('')

const isFormValid = computed(() => {
  return form.username.trim() && 
         form.email && 
         form.password.length >= 8 &&
         form.confirmPassword === form.password &&
         Object.keys(errors.value).length === 0
})

const passwordStrength = computed(() => {
  const pwd = form.password
  let score = 0
  if (pwd.length >= 8) score++
  if (/[a-z]/.test(pwd)) score++
  if (/[A-Z]/.test(pwd)) score++
  if (/\d/.test(pwd)) score++
  if (/[^a-zA-Z\d]/.test(pwd)) score++
  return score
})

const passwordStrengthClass = computed(() => {
  const score = passwordStrength.value
  if (score <= 2) return 'weak'
  if (score <= 3) return 'medium'
  return 'strong'
})

const passwordStrengthText = computed(() => {
  const score = passwordStrength.value
  if (score <= 2) return '弱'
  if (score <= 3) return '中等'
  return '强'
})

const validateForm = () => {
  errors.value = {}
  let valid = true

  if (!form.username.trim()) {
    errors.value.username = '用户名不能为空'
    valid = false
  } else if (form.username.length < 3) {
    errors.value.username = '用户名至少3个字符'
    valid = false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email || !emailRegex.test(form.email)) {
    errors.value.email = '请输入有效的邮箱地址'
    valid = false
  }

  if (form.password.length < 8) {
    errors.value.password = '密码至少8位字符'
    valid = false
  }

  if (form.password && form.confirmPassword && form.password !== form.confirmPassword) {
    errors.value.confirmPassword = '两次输入密码不一致'
    valid = false
  }

  return valid
}

const validatePassword = () => {
  if (form.password.length < 8) {
    errors.value.password = '密码至少8位字符'
  } else {
    delete errors.value.password
  }
}

const validateConfirmPassword = () => {
  if (form.confirmPassword && form.password !== form.confirmPassword) {
    errors.value.confirmPassword = '两次输入密码不一致'
  } else {
    delete errors.value.confirmPassword
  }
}

const handleRegister = async () => {
  if (!validateForm()) return
  
  globalError.value = ''
  authStore.clearError()
  
  try {
    await authStore.register({
      username: form.username,
      email: form.email,
      password: form.password
    })
    // Success handled in store redirect
  } catch (err) {
    globalError.value = authError.value || '注册失败，请重试'
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

const successMode = computed(() => route.query.success === 'true')

const successMessage = ref('')

onMounted(async () => {
  console.log('欢迎注册虚拟点交易平台! ✨')
  authStore.clearError()
  authStore.fetchProviders()
  if (successMode.value) {
    successMessage.value = '注册成功！您现在可以登录了...'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  }
  await nextTick()
  if (!successMode.value) {
    const usernameInput = document.getElementById('username')
    if (usernameInput) usernameInput.focus()
  }
})
</script>

<style scoped>
/* ... existing styles ... password strength colors */
.password-strength {
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 4px;
  margin-top: 4px;
}

.password-strength.weak {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.password-strength.medium {
  background: rgba(251, 191, 36, 0.2);
  color: #f59e0b;
}

.password-strength.strong {
  background: rgba(34, 197, 94, 0.2);
  color: #10b981;
}

.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: 'Segoe UI', sans-serif;
}

.register-box {
  display: flex;
  width: 800px;
  max-width: 100%;
  background: #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 25px 75px rgba(0, 0, 0, 0.6);
}

.register-branding {
  flex: 1;
  background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%);
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.brand-title {
  font-size: 36px;
  font-weight: 800;
  color: #fff;
  margin: 0 0 16px 0;
  background: linear-gradient(45deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  line-height: 1.5;
}

.register-form-section {
  flex: 1;
  padding: 50px;
  background: #252526;
}

.form-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #e0e0e0;
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 15px;
  color: #8e8e8e;
  margin: 0;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group label {
  font-size: 14px;
  font-weight: 600;
  color: #d4d4d4;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #8e8e8e;
  font-size: 16px;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 14px 16px 14px 44px;
  background: #3c3c3c;
  border: 2px solid #3c3c3c;
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 15px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.input-wrapper input:focus {
  border-color: #4dabf7;
  box-shadow: 0 0 0 3px rgba(77, 171, 247, 0.1);
  background: #404040;
  outline: none;
}

.input-wrapper input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #8e8e8e;
  cursor: pointer;
  padding: 4px;
  font-size: 16px;
}

.password-toggle:hover {
  color: #e0e0e0;
}

.field-error {
  color: #f87171;
  font-size: 13px;
  margin-top: 4px;
}

.error-message {
  background: rgba(248, 113, 113, 0.15);
  border: 1px solid rgba(248, 113, 113, 0.3);
  border-radius: 8px;
  padding: 12px 16px;
  color: #f87171;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.success-title {
  color: #10b981 !important;
}

.success-subtitle {
  color: #6ee7b7 !important;
  font-weight: 500;
}

.success-message {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
  padding: 20px;
  color: #10b981;
  font-size: 16px;
  text-align: center;
  line-height: 1.5;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.success-message i {
  font-size: 24px;
}

.register-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 8px;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
}

.register-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.divider {
  position: relative;
  text-align: center;
  margin: 32px 0;
  color: #8e8e8e;
  font-size: 14px;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #404040;
}

.divider span {
  background: #252526;
  padding: 0 24px;
  position: relative;
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.social-btn {
  padding: 12px 20px;
  background: #2d2d30;
  border: 2px solid #404040;
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.social-btn:hover:not(:disabled) {
  background: #404040;
  border-color: #4dabf7;
  transform: translateY(-1px);
}

.social-btn i {
  font-size: 20px;
}

.social-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-section {
  margin-top: 32px;
  text-align: center;
  font-size: 15px;
  color: #8e8e8e;
}

.login-link {
  color: #4dabf7;
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
}

.login-link:hover {
  text-decoration: underline;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .register-box {
    flex-direction: column;
    margin: 10px;
  }
  
  .register-branding, .register-form-section {
    padding: 40px 30px;
  }
  
  .brand-title {
    font-size: 28px;
  }
}
</style>
