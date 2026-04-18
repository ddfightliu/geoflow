<template>
  <div class="home-dashboard">
    <header class="dashboard-header">
      <h1>虚拟点交易平台</h1>
      <p>欢迎回来！您的虚拟点交易中心</p>
    </header>

    <div v-if="!user" class="login-prompt">
      <h2>请先登录以查看您的虚拟点余额和交易记录</h2>
      <router-link to="/login" class="login-cta">立即登录</router-link>
    </div>

    <div v-else class="dashboard-content">
      <!-- Points Balance Card -->
      <div class="points-card">
        <div class="card-header">
          <h3>虚拟点余额</h3>
          <span class="points-value">{{ user.points || 0 }} 点</span>
        </div>
        <div class="card-actions">
          <button class="action-btn buy-btn" @click="openBuyModal">
            <i class="fas fa-plus-circle"></i> 购买虚拟点
          </button>
          <button class="action-btn sell-btn" @click="openSellModal">
            <i class="fas fa-minus-circle"></i> 出售虚拟点
          </button>
        </div>
      </div>

      <!-- Market Price Card -->
      <div class="market-card">
        <div class="card-header">
          <h3>实时市场价格</h3>
          <span class="market-price">{{ marketPrice }} 元/点</span>
        </div>
        <div class="market-info">
          <p>24h 变化: <span class="change positive">+2.5%</span></p>
          <p>最高: {{ (marketPrice * 1.05).toFixed(2) }} | 最低: {{ (marketPrice * 0.95).toFixed(2) }}</p>
        </div>
      </div>

      <!-- Recent Transactions -->
      <div class="transactions-card">
        <div class="card-header">
          <h3>最近交易 (5条)</h3>
          <router-link to="/transactions" class="view-all">查看全部 →</router-link>
        </div>
        <div v-if="transactions.length" class="transactions-list">
          <div v-for="tx in transactions.slice(0, 5)" :key="tx.id" class="transaction-item">
            <div :class="['tx-type', tx.type === 'buy' ? 'buy' : 'sell']">
              {{ tx.type === 'buy' ? '购买' : '出售' }}
            </div>
            <div class="tx-details">
              <span class="tx-points">{{ tx.points }} 点</span>
              <span class="tx-price">{{ tx.totalPrice }} 元</span>
              <span class="tx-time">{{ formatTime(tx.created_at) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-transactions">
          <p>暂无交易记录</p>
          <p>快去买点虚拟点开始交易吧！</p>
        </div>
      </div>
    </div>

    <!-- Buy Modal -->
    <div v-if="showBuyModal" class="modal-overlay" @click="closeModals">
      <div class="modal" @click.stop>
        <h3>购买虚拟点</h3>
        <form @submit.prevent="buyPoints">
          <div class="input-group">
            <label>购买数量 (点)</label>
            <input v-model.number="buyForm.quantity" type="number" min="100" max="100000" required />
          </div>
          <div class="input-group">
            <label>单价 (元/点)</label>
            <input v-model.number="buyForm.price" type="number" step="0.01" min="0.01" required />
          </div>
          <div class="total-cost">
            总计: {{ calculateTotal(buyForm) }} 元 (手续费 {{ calculateFee(buyForm) }})
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModals" class="cancel-btn">取消</button>
            <button type="submit" class="confirm-btn" :disabled="!isBuyFormValid">
              确认购买
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Sell Modal -->
    <div v-if="showSellModal" class="modal-overlay" @click="closeModals">
      <div class="modal" @click.stop>
        <h3>出售虚拟点</h3>
        <form @submit.prevent="sellPoints">
          <div class="input-group">
            <label>出售数量 (点)</label>
            <input v-model.number="sellForm.quantity" type="number" min="100" :max="user.points || 0" required />
          </div>
          <div class="input-group">
            <label>单价 (元/点)</label>
            <input v-model.number="sellForm.price" type="number" step="0.01" min="0.01" required />
          </div>
          <div class="total-cost">
            预计收入: {{ calculateTotal(sellForm) }} 元 (手续费 {{ calculateFee(sellForm) }})
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModals" class="cancel-btn">取消</button>
            <button type="submit" class="confirm-btn" :disabled="!isSellFormValid">
              确认出售
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'pinia'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'HomeView',
  data() {
    return {
      marketPrice: 0.12,
      transactions: [],
      showBuyModal: false,
      showSellModal: false,
      buyForm: { quantity: 1000, price: 0.12 },
      sellForm: { quantity: 1000, price: 0.11 }
    }
  },
  computed: {
    ...mapState(useAuthStore, ['user', 'loading']),
    ...mapGetters(useAuthStore, ['isAuthenticated']),
    isBuyFormValid() {
      return this.buyForm.quantity >= 100 && this.buyForm.price > 0
    },
    isSellFormValid() {
      return this.sellForm.quantity >= 100 && this.sellForm.quantity <= (this.user.points || 0) && this.sellForm.price > 0
    }
  },
  methods: {
    ...mapActions(useAuthStore, ['fetchPointsBalance', 'buyVirtualPoints', 'sellVirtualPoints']),

    openBuyModal() {
      this.showBuyModal = true
    },

    openSellModal() {
      this.showSellModal = true
    },

    closeModals() {
      this.showBuyModal = false
      this.showSellModal = false
    },

    calculateTotal(form) {
      if (!form.quantity || !form.price) return 0
      return (form.quantity * form.price).toFixed(2)
    },

    calculateFee(form) {
      if (!form.quantity || !form.price) return 0
      const total = form.quantity * form.price
      return (total * 0.01).toFixed(2) // 1% fee
    },

    formatTime(timeStr) {
      return new Date(timeStr).toLocaleString('zh-CN', { hour12: false })
    },

    async buyPoints() {
      if (!this.isBuyFormValid) return
      try {
        await this.buyVirtualPoints(this.buyForm)
        this.closeModals()
        // Refresh balance
        await this.fetchPointsBalance()
      } catch (error) {
        console.error('购买失败', error)
      }
    },

    async sellPoints() {
      if (!this.isSellFormValid) return
      try {
        await this.sellVirtualPoints(this.sellForm)
        this.closeModals()
        // Refresh balance
        await this.fetchPointsBalance()
      } catch (error) {
        console.error('出售失败', error)
      }
    }
  },
  async mounted() {
    if (this.isAuthenticated) {
      await this.fetchPointsBalance()
      // Mock recent transactions
      this.transactions = [
        {
          id: 1,
          type: 'buy',
          points: 5000,
          price: 0.12,
          totalPrice: '600.00',
          created_at: '2024-10-20T10:30:00'
        },
        {
          id: 2,
          type: 'sell',
          points: 2000,
          price: 0.11,
          totalPrice: '220.00',
          created_at: '2024-10-19T15:45:00'
        },
        {
          id: 3,
          type: 'buy',
          points: 3000,
          price: 0.115,
          totalPrice: '345.00',
          created_at: '2024-10-18T09:15:00'
        }
      ]
    }
  }
}
</script>

<style scoped>
.home-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  color: white;
  padding: 20px;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
}

.dashboard-header {
  text-align: center;
  padding: 40px 20px;
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  margin-bottom: 40px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.dashboard-header h1 {
  font-size: 36px;
  font-weight: 800;
  margin: 0 0 12px 0;
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard-header p {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
  max-width: 600px;
}

.login-prompt {
  text-align: center;
  padding: 80px 40px;
  background: rgba(255,255,255,0.05);
  border-radius: 24px;
  max-width: 500px;
  margin: 0 auto;
  backdrop-filter: blur(10px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.login-cta {
  display: inline-block;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
  padding: 16px 40px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  margin-top: 32px;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
}

.login-cta:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(79, 70, 229, 0.5);
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.points-card, .market-card, .transactions-card {
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid rgba(255,255,255,0.1);
  transition: all 0.4s ease;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.points-card:hover, .market-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}

.transactions-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 20px;
}

.card-header h3 {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: #e0e0e0;
}

.points-value {
  font-size: 42px;
  font-weight: 900;
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(78, 205, 196, 0.5);
}

.market-price {
  font-size: 32px;
  font-weight: 800;
  color: #4ecdc4;
  text-shadow: 0 0 20px rgba(78, 205, 196, 0.3);
}

.card-actions {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.action-btn {
  flex: 1;
  padding: 18px 24px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 15px;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.buy-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.buy-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 35px rgba(16, 185, 129, 0.4);
}

.sell-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.sell-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 35px rgba(239, 68, 68, 0.4);
}

.market-info p {
  margin: 8px 0;
  opacity: 0.9;
}

.change {
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 14px;
}

.positive {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.transaction-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255,255,255,0.05);
  border-radius: 16px;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.transaction-item:hover {
  background: rgba(255,255,255,0.1);
  transform: translateX(4px);
}

.tx-type {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  color: white;
  min-width: 60px;
  text-align: center;
}

.tx-type.buy {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.tx-type.sell {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.tx-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tx-points {
  font-size: 18px;
  font-weight: 600;
  color: #e0e0e0;
}

.tx-price {
  color: #4ecdc4;
  font-weight: 700;
  font-size: 16px;
}

.tx-time {
  opacity: 0.7;
  font-size: 13px;
}

.no-transactions {
  text-align: center;
  padding: 60px 20px;
  color: #a0a0a0;
}

.no-transactions p {
  margin: 12px 0;
}

.no-transactions p:last-child {
  font-weight: 600;
  color: #4ecdc4;
  font-size: 16px;
}

.view-all {
  color: #4dabf7;
  text-decoration: none;
  font-weight: 700;
  font-size: 14px;
  transition: color 0.2s;
}

.view-all:hover {
  color: #60a5fa;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.modal {
  background: #1e1e1e;
  padding: 48px;
  border-radius: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid rgba(255,255,255,0.15);
  box-shadow: 0 25px 80px rgba(0,0,0,0.6);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal h3 {
  margin: 0 0 32px 0;
  font-size: 28px;
  color: #e0e0e0;
  text-align: center;
  font-weight: 700;
}

.input-group {
  margin-bottom: 24px;
}

.input-group label {
  display: block;
  margin-bottom: 12px;
  color: #d4d4d4;
  font-weight: 600;
  font-size: 15px;
}

.input-group input {
  width: 100%;
  padding: 16px 20px;
  background: #2d2d2e;
  border: 2px solid #404040;
  border-radius: 12px;
  color: #e0e0e0;
  font-size: 17px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.input-group input:focus {
  border-color: #4dabf7;
  outline: none;
  box-shadow: 0 0 0 3px rgba(77, 171, 247, 0.1);
  background: #353537;
}

.total-cost {
  background: rgba(78, 205, 196, 0.15);
  padding: 20px;
  border-radius: 16px;
  text-align: center;
  font-size: 24px;
  font-weight: 800;
  color: #4ecdc4;
  margin: 24px 0;
  border: 2px solid rgba(78, 205, 196, 0.3);
  box-shadow: 0 4px 20px rgba(78, 205, 196, 0.1);
}

.modal-actions {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}

.cancel-btn, .confirm-btn {
  flex: 1;
  padding: 16px 32px;
  border-radius: 16px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.cancel-btn {
  background: #404040;
  color: #e0e0e0;
}

.cancel-btn:hover {
  background: #505050;
  transform: translateY(-2px);
}

.confirm-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(16, 185, 129, 0.4);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .dashboard-content {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 0 10px;
  }
  
  .dashboard-header {
    padding: 30px 15px;
  }
  
  .dashboard-header h1 {
    font-size: 28px;
  }
  
  .modal {
    margin: 20px;
    padding: 32px 24px;
  }
}
</style>

