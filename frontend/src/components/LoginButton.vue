<template>
  <button 
    class="login-button" 
    :class="[`login-button--${provider}`, { 'login-button--disabled': disabled }]"
    :disabled="disabled"
    @click="handleClick"
  >
    <span class="login-button__icon">
      <i :class="iconClass"></i>
    </span>
    <span class="login-button__text">{{ text }}</span>
  </button>
</template>

<script>
export default {
  name: 'LoginButton',
  props: {
    provider: {
      type: String,
      required: true
    },
    text: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    iconClass() {
      const icons = {
        github: 'fab fa-github',
        microsoft: 'fab fa-microsoft',
        feishu: 'icon-feishu',
        wechat: 'fab fa-weixin',
        alipay: 'icon-alipay',
        douyin: 'icon-douyin'
      }
      return icons[this.provider] || 'fas fa-user'
    }
  },
  methods: {
    handleClick() {
      if (!this.disabled) {
        this.$emit('click', this.provider)
      }
    }
  }
}
</script>

<style scoped>
.login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #fff;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-button--github {
  background-color: #24292e;
}

.login-button--microsoft {
  background-color: #0078d4;
}

.login-button--feishu {
  background-color: #29a1f1;
}

.login-button--wechat {
  background-color: #07c160;
}

.login-button--alipay {
  background-color: #1677ff;
}

.login-button--douyin {
  background-color: #000000;
}

.login-button__icon {
  font-size: 20px;
}

.login-button__text {
  flex: 1;
  text-align: center;
}

/* Custom icons */
.icon-feishu::before {
  content: "飞书";
  font-size: 14px;
  font-weight: bold;
}

.icon-alipay::before {
  content: "支";
  font-size: 16px;
  font-weight: bold;
}

.icon-douyin::before {
  content: "抖";
  font-size: 16px;
  font-weight: bold;
}
</style>

