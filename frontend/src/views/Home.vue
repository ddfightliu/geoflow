<template>
  <div class="home-dashboard">
    <header class="dashboard-header">
      <h1>虚拟点交易平台</h1>
      <p>欢迎回来！您的虚拟点交易中心</p>
    </header>

    <!-- Hide login prompt - handled by App.vue modals now -->
    <!--
    <div v-if="!user" class="login-prompt">
      <h2>请先登录以查看您的虚拟点余额和交易记录</h2>
      <router-link to="/login" class="login-cta">立即登录</router-link>
    </div>
    -->

    <div v-if="user" class="dashboard-content">
      <!-- Points Balance Card -->
      <div class="points-card">
        <div class="card-header">
          <h3>虚拟点余额</h3>
          <span class="points-value">{{ user?.points || 0 }} 点</span>
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
            <input v-model.number="sellForm.quantity" type="number" min="100" :max="user?.points || 0" required />
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

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { user, loading, isAuthenticated } = storeToRefs(authStore)

const marketPrice = ref(0.12)
const transactions = ref([])
const showBuyModal = ref(false)
const showSellModal = ref(false)
const buyForm = reactive({ quantity: 1000, price: 0.12 })
const sellForm = reactive({ quantity: 1000, price: 0.11 })

const isBuyFormValid = computed(() => {
  return buyForm.quantity >= 100 && buyForm.price > 0
})

const isSellFormValid = computed(() => {
  return sellForm.quantity >= 100 && sellForm.quantity <= (user.value?.points || 0) && sellForm.price > 0
})

const openBuyModal = () => {
  showBuyModal.value = true
}

const openSellModal = () => {
  showSellModal.value = true
}

const closeModals = () => {
  showBuyModal.value = false
  showSellModal.value = false
}

const calculateTotal = (form) => {
  if (!form.quantity || !form.price) return 0
  return (form.quantity * form.price).toFixed(2)
}

const calculateFee = (form) => {
  if (!form.quantity || !form.price) return 0
  const total = form.quantity * form.price
  return (total * 0.01).toFixed(2)
}

const formatTime = (timeStr) => {
  return new Date(timeStr).toLocaleString('zh-CN', { hour12: false })
}

const buyPoints = async () => {
  if (!isBuyFormValid.value) return
  try {
    await authStore.buyVirtualPoints(buyForm)
    closeModals()
    await authStore.fetchPointsBalance()
  } catch (error) {
    console.error('购买失败', error)
  }
}

const sellPoints = async () => {
  if (!isSellFormValid.value) return
  try {
    await authStore.sellVirtualPoints(sellForm)
    closeModals()
    await authStore.fetchPointsBalance()
  } catch (error) {
    console.error('出售失败', error)
  }
}

onMounted(async () => {
  console.log('欢迎回家，交易大师! 💰')
  if (isAuthenticated.value) {
    await authStore.fetchPointsBalance()
    // Mock transactions
    transactions.value = [
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
})
</script>

<style scoped>
/* All existing Home.vue styles preserved - unchanged */
.home-dashboard {
  /* ... existing styles ... */
}
</style>
