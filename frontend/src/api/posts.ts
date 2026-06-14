import { api } from './client'
import type { Post } from '@/types'

// 后端字段（snake_case）→ 前端类型（camelCase）
function adapt(raw: any): Post {
  return {
    slug:        raw.slug,
    title:       raw.title,
    summary:     raw.summary,
    content:     raw.content,
    tags:        raw.tags ? raw.tags.split(',').map((t: string) => t.trim()).filter(Boolean) : [],
    createdAt:   raw.created_at,
    readingTime: raw.reading_time,
    viewCount:   raw.view_count ?? 0,
    cover:       raw.cover,
  }
}

export const postsApi = {
  list(params?: { page?: number; tag?: string }): Promise<Post[]> {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.tag)  q.set('tag', params.tag)
    return api.get<any[]>(`/api/posts?${q}`).then(r => r.map(adapt))
  },

  get(slug: string): Promise<Post> {
    return api.get<any>(`/api/posts/${slug}`).then(adapt)
  },

  create(data: {
    slug: string; title: string; summary: string; content: string
    tags: string; reading_time: number; published: boolean
  }): Promise<Post> {
    return api.post<any>('/api/posts', data).then(adapt)
  },

  update(slug: string, data: Partial<{
    title: string; summary: string; content: string
    tags: string; reading_time: number; published: boolean
  }>): Promise<Post> {
    return api.patch<any>(`/api/posts/${slug}`, data).then(adapt)
  },

  delete(slug: string): Promise<void> {
    return api.delete(`/api/posts/${slug}`)
  },

  adjacent(slug: string): Promise<{ prev: { slug: string; title: string } | null; next: { slug: string; title: string } | null }> {
    return api.get(`/api/posts/${slug}/adjacent`)
  },
}
