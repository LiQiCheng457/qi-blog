import { api } from './client'

export interface Wish {
  id: number
  content: string
  is_seed: boolean
  resonance_count: number
  has_resonated: boolean
  created_at: string
}

export interface WishAdmin {
  id: number
  content: string
  user_id: number | null
  username: string | null
  is_seed: boolean
  resonance_count: number
  created_at: string
}

export const wishesApi = {
  stats:    () => api.get<{ total: number }>('/api/wishes/stats'),
  random:   (excludeId?: number) =>
    api.get<Wish>(`/api/wishes/random${excludeId ? `?exclude=${excludeId}` : ''}`),
  create:   (content: string) => api.post<Wish>('/api/wishes', { content }),
  resonate: (id: number)      => api.post<Wish>(`/api/wishes/${id}/resonate`, {}),

  adminList:   ()        => api.get<WishAdmin[]>('/api/wishes/admin/list'),
  adminDelete: (id: number) => api.delete<{ message: string }>(`/api/wishes/admin/${id}`),
  adminClear:  ()        => api.delete<{ cleared: number }>('/api/wishes/admin/clear/all'),
}
