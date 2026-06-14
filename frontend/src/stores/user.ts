/**
 * 统一用户 Store：管理员和普通用户共用同一套登录状态
 * role='admin' → 可访问后台管理
 * role='user'  → 可评论
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usersApi, type AppUser } from '@/api/users'

const TOKEN_KEY = 'qi_token'

export const useUserStore = defineStore('user', () => {
  const token   = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const profile = ref<AppUser | null>(null)

  const isLoggedIn = computed(() => !!token.value && !!profile.value)
  const isAdmin    = computed(() => profile.value?.role === 'admin')

  async function init() {
    if (!token.value) return
    try {
      profile.value = await usersApi.me(token.value)
    } catch {
      token.value = null
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  async function login(login: string, password: string) {
    const res = await usersApi.login(login, password)
    token.value = res.token
    profile.value = res.user
    localStorage.setItem(TOKEN_KEY, res.token)
  }

  async function register(username: string, email: string, password: string) {
    await usersApi.register(username, email, password)
    await login(email, password)
  }

  async function updateProfile(data: { username?: string; bio?: string; avatar?: string }) {
    profile.value = await usersApi.updateMe(data)
  }

  function logout() {
    token.value = null
    profile.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { token, profile, isLoggedIn, isAdmin, init, login, register, updateProfile, logout }
})
