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

export const usersApi = {
  async register(username: string, email: string, password: string): Promise<AppUser> {
    return api.post<any>('/api/users/register', { username, email, password }).then(adaptUser)
  },

  async login(login: string, password: string): Promise<{ token: string; user: AppUser }> {
    const data = await api.post<any>('/api/users/login', { login, password })
    return { token: data.access_token, user: adaptUser(data.user) }
  },

  async me(): Promise<AppUser> {
    return api.get<any>('/api/users/me').then(adaptUser)
  },

  async updateMe(data: { username?: string; bio?: string; avatar?: string }): Promise<AppUser> {
    return api.patch<any>('/api/users/me', data).then(adaptUser)
  },
}

// 向后兼容的别名
export type ReaderUser = AppUser
