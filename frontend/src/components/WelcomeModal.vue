<template>
  <div class="welcome-overlay" @click.self="handleLater">
    <div class="welcome-modal">
      <div class="welcome-header">
        <div class="welcome-icon">🚀</div>
        <h2>欢迎来到虚拟点交易平台</h2>
        <p class="welcome-subtitle">专业的虚拟点交易中心</p>
      </div>

      <div class="welcome-features">
        <div class="feature-item">
          <i class="fas fa-coins"></i>
          <div>
            <h4>实时交易</h4>
            <p>即时买卖虚拟点，价格透明</p>
          </div>
        </div>
        <div class="feature-item">
          <i class="fas fa-shield-alt"></i>
          <div>
            <h4>安全保障</h4>
            <p>多重安全机制保护您的资产</p>
          </div>
        </div>
        <div class="feature-item">
          <i class="fas fa-chart-line"></i>
          <div>
            <h4>市场分析</h4>
            <p>专业数据分析，助您把握商机</p>
          </div>
        </div>
      </div>

      <div class="welcome-actions">
        <button class="login-btn" @click="handleLogin">
          <i class="fas fa-sign-in-alt"></i>
          立即登录
        </button>
        <button class="later-btn" @click="handleLater">
          稍后再说
        </button>
      </div>

      <div class="welcome-footer">
        <span class="register-link" @click.stop="handleRegister">
          没有账户？立即注册
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits } from 'vue'

const emit = defineEmits(['login', 'close', 'register'])

const handleLogin = () => {
  emit('login')
}

const handleLater = () => {
  emit('close')
}

const handleRegister = () => {
  emit('register')
}
</script>

<style scoped>
.welcome-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(8px);
  animation: fadeIn 0.3s ease-out;
}

.welcome-modal {
  background: linear-gradient(135deg, #1e1e1e 0%, #252526 100%);
  border-radius: 16px;
  padding: 40px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: slideUp 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.welcome-header {
  text-align: center;
  margin-bottom: 32px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.welcome-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 16px;
  color: #cccccc;
  margin: 0;
}

.welcome-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
}

.feature-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.feature-item i {
  font-size: 24px;
  color: #4ecdc4;
  margin-top: 2px;
  flex-shrink: 0;
}

.feature-item h4 {
  font-size: 16px;
  font-weight: 600;
  color: #e0e0e0;
  margin: 0 0 4px 0;
}

.feature-item p {
  font-size: 14px;
  color: #999999;
  margin: 0;
  line-height: 1.5;
}

.welcome-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, #0078d4, #005a9e);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 120, 212, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(0, 120, 212, 0.4);
}

.later-btn {
  width: 100%;
  padding: 12px 24px;
  background: transparent;
  border: 2px solid #404040;
  border-radius: 10px;
  color: #cccccc;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.later-btn:hover {
  border-color: #0078d4;
  color: #0078d4;
  background: rgba(0, 120, 212, 0.1);
}

.welcome-footer {
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
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 600px) {
  .welcome-modal {
    padding: 30px 24px;
    margin: 20px;
  }
  
  .welcome-header h2 {
    font-size: 24px;
  }
}
</style>

