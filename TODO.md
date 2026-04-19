# New Tasks: Forgot Password + Console Welcomes

Status: **Planning** 

## Tasks
1. **Fix run_geoflow.py** - Remove `--api` flag (Vite error), fix readiness check
2. **Forgot Password**:
   - Login.vue: "忘记密码?" → input modal → authStore.forgotPassword(email)
   - Store already has action (backend mock OK)
   - Show toast "重置邮件发送成功"
3. **Console Welcome Messages** - Add `console.log` in onMounted:
   - Login.vue: "欢迎来到登录页面! 👋"
   - Register.vue: "欢迎注册虚拟点交易平台! ✨"
   - Home.vue: "欢迎回家，交易大师! 💰"
   - App.vue: "GeoFlow App loaded! 🚀"

## Files
- run_geoflow.py
- frontend/src/views/Login.vue (add forgot modal)
- All Vue pages (add console.log)

