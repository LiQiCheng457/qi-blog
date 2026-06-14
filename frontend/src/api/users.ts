import { api } from './client'

export interface AppUser {
  id: number
  username: string
  email: string
  role: 'user' | 'admin'
  avatar?: string
  bio?: string
  createdAt: string
}

function adaptUser(raw: any): AppUser {
  return {
    id: raw.id,
    username: raw.username,
    email: raw.email,
    role: raw.role ?? 'user',
    avatar: raw.avatar,
    bio: raw.bio,
    createdAt: raw.created_at,
  }
}

const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export const usersApi = {
  async register(username: string, email: string, password: string): Promise<AppUser> {
    return api.post<any>('/api/users/register', { username, email, password }).then(adaptUser)
  },

  async login(login: string, password: string): Promise<{ token: string; user: AppUser }> {
    const res = await fetch(`${BASE}/api/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '登录失败' }))
      throw new Error(err.detail ?? '登录失败')
    }
    const data = await res.json()
    return { token: data.access_token, user: adaptUser(data.user) }
  },

  async me(token: string): Promise<AppUser> {
    const res = await fetch(`${BASE}/api/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('未登录')
    return res.json().then(adaptUser)
  },

  async updateMe(data: { username?: string; bio?: string; avatar?: string }): Promise<AppUser> {
    return api.patch<any>('/api/users/me', data).then(adaptUser)
  },
}

// 向后兼容的别名
export type ReaderUser = AppUser
