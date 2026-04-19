<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <h3>用户登录</h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="$emit('login', { username: username, password: password, remember_me: rememberMe })" class="login-form">
        <div class="input-group">
          <label>用户名</label>
          <div class="input-wrapper">
            <i class="fas fa-user input-icon"></i>
            <input
              v-model="username"
              type="text"
              placeholder="请输入用户名或邮箱"
              :disabled="loading"
              required
            />
          </div>
        </div>

        <div class="input-group">
          <label>密码</label>
          <div class="input-wrapper">
            <i class="fas fa-lock input-icon"></i>
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              :disabled="loading"
              required
            />
            <button type="button" class="password-toggle" @click="showPassword = !showPassword">
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
        </div>

        <div class="form-options">
          <label class="checkbox-label">
            <input type="checkbox" v-model="rememberMe" />
            <span>记住我</span>
          </label>
        </div>

        <div v-if="error" class="error-message">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else><i class="fas fa-sign-in-alt"></i> 登录</span>
        </button>
      </form>

      <div class="divider">
        <span>或使用第三方登录</span>
      </div>

      <div class="social-login">
        <button
          v-for="provider in providers"
          :key="provider.id"
          class="social-btn"
          :disabled="!provider.enabled || loading"
          @click="$emit('social-login', provider.id)"
        >
          <i :class="getProviderIcon(provider.id)"></i>
          {{ provider.name }}
        </button>
      </div>

      <div class="modal-footer">
        <router-link to="/register" class="register-link" @click="$emit('close')">
          没有账户？立即注册
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, defineProps, watch } from 'vue'

const props = defineProps({
  loading: Boolean,
  error: String,
  providers: Array
})

const emit = defineEmits(['close', 'login', 'social-login'])

const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)

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
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2001;
  backdrop-filter: blur(10px);
  animation: fadeIn 0.3s ease-out;
}

.modal {
  background: #252526;
  border-radius: 12px;
  width: 90%;
  max-width: 420px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: slideUp 0.4s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  margin-bottom: 16px;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #e0e0e0;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #808080;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #cccccc;
}

.login-form {
  padding: 0 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group label {
  font-size: 14px;
  font-weight: 500;
  color: #cccccc;
  margin-bottom: 6px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: #808080;
  font-size: 14px;
  z-index: 1;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 14px 12px 40px;
  background: #3c3c3c;
  border: 1px solid #3c3c3c;
  border-radius: 6px;
  color: #cccccc;
  font-size: 14px;
}

.input-wrapper input:focus {
  border-color: #0078d4;
  box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
  outline: none;
}

.input-wrapper input::placeholder {
  color: #6e6e6e;
}

.input-wrapper input:disabled {
  opacity: 0.6;
}

.password-toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #808080;
  cursor: pointer;
}

.form-options {
  display: flex;
  justify-content: flex-start;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #cccccc;
}

.checkbox-label input[type='checkbox'] {
  width: 16px;
  height: 16px;
  accent-color: #0078d4;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(247, 82, 73, 0.15);
  border: 1px solid rgba(247, 82, 73, 0.4);
  border-radius: 6px;
  color: #f75249;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #0078d4, #005a9e);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 120, 212, 0.4);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.divider {
  padding: 0 24px;
  display: flex;
  align-items: center;
  margin: 20px 0;
  color: #808080;
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #404040;
}

.divider span {
  padding: 0 16px;
  white-space: nowrap;
}

.social-login {
  padding: 0 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.social-btn {
  padding: 12px 16px;
  background: #3c3c3c;
  border: 1px solid #484848;
  border-radius: 6px;
  color: #e0e0e0;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s;
}

.social-btn:hover:not(:disabled) {
  background: #484848;
  border-color: #0078d4;
}

.social-btn i {
  font-size: 16px;
}

.social-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-footer {
  padding: 0 24px 24px;
  text-align: center;
}

.register-link {
  color: #0078d4;
  font-size: 14px;
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .modal {
    margin: 20px;
    border-radius: 8px;
  }
}
</style>

