/**
 * Pinia Auth Store
 * Manages user authentication state
 */

import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    providers: [],
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user,
    availableProviders: (state) => state.providers.filter(p => p.enabled)
  },

  actions: {
    async fetchProviders() {
      try {
        const response = await axios.get(`${API_BASE}/api/auth/providers`)
        this.providers = response.data.providers
      } catch (error) {
        console.error('Failed to fetch providers:', error)
        this.error = 'Failed to load login options'
      }
    },

    async loginWithProvider(provider) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/api/auth/login/${provider}`)
        // Redirect to OAuth provider
        window.location.href = response.data.authorization_url
      } catch (error) {
        console.error('Login failed:', error)
        this.error = 'Failed to initiate login'
        this.loading = false
      }
    },

    async loginWithCredentials({ username, password, remember_me = false }) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/api/auth/login`, {
          username,
          password,
          remember_me
        })
        
        const { access_token, user } = response.data
        this.token = access_token
        this.user = user
        
        if (remember_me) {
          localStorage.setItem('token', access_token)
        } else {
          sessionStorage.setItem('token', access_token)
        }
        
        this.loading = false
        return { success: true }
      } catch (error) {
        console.error('Login failed:', error)
        this.error = error.response?.data?.detail || 'Login failed. Please check your credentials.'
        this.loading = false
        return { success: false, error: this.error }
      }
    },

    async fetchCurrentUser() {
      if (!this.token) return null
      
      try {
        const response = await axios.get(`${API_BASE}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        this.user = response.data
        return response.data
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.logout()
        return null
      }
    },

    async setToken(token) {
      this.token = token
      this.loading = true
      localStorage.setItem('token', token)
      await this.fetchCurrentUser()
      this.loading = false
    },

    logout() {
      this.user = null
      this.token = null
      this.loading = false
      this.error = null
      localStorage.removeItem('token')
    },

    clearError() {
      this.error = null
    }
  }
})

