import { api } from './client'

export interface Comment {
  id: number
  postSlug: string
  userId: number
  username: string
  avatar?: string
  role: string
  content: string
  parentId?: number
  createdAt: string
}

function adapt(raw: any): Comment {
  return {
    id: raw.id,
    postSlug: raw.post_slug,
    userId: raw.user_id,
    username: raw.username,
    avatar: raw.avatar,
    role: raw.role ?? 'user',
    content: raw.content,
    parentId: raw.parent_id,
    createdAt: raw.created_at,
  }
}

export const commentsApi = {
  list(postSlug: string): Promise<Comment[]> {
    return api.get<any[]>(`/api/comments/${postSlug}`).then(r => r.map(adapt))
  },

  create(postSlug: string, content: string, parentId?: number): Promise<Comment> {
    return api.post<any>(`/api/comments/${postSlug}`, { content, parent_id: parentId ?? null }).then(adapt)
  },

  delete(commentId: number): Promise<void> {
    return api.delete(`/api/comments/${commentId}`)
  },

  adminDelete(commentId: number): Promise<void> {
    return api.delete(`/api/comments/admin/${commentId}`)
  },
}
