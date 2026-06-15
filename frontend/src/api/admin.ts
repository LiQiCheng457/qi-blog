import { api } from './client'

export interface MonthStat  { month: string; count: number }
export interface TopPost    { title: string; views: number }
export interface ActiveChatter {
  user_id: number; username: string; avatar?: string
  msg_count: number; last_at: string | null
}

export interface DashboardStats {
  postCount: number
  pubCount: number
  viewTotal: number
  commentCount: number
  userCount: number
  monthlyPosts: MonthStat[]
  monthlyComments: MonthStat[]
  topPosts: TopPost[]
  chatMsgCount: number
  chatUserCount: number
  monthlyChats: MonthStat[]
  activeChatters: ActiveChatter[]
}

function adapt(raw: any): DashboardStats {
  return {
    postCount:       raw.post_count,
    pubCount:        raw.pub_count,
    viewTotal:       raw.view_total,
    commentCount:    raw.comment_count,
    userCount:       raw.user_count,
    monthlyPosts:    raw.monthly_posts,
    monthlyComments: raw.monthly_comments,
    topPosts:        raw.top_posts,
    chatMsgCount:    raw.chat_msg_count   ?? 0,
    chatUserCount:   raw.chat_user_count  ?? 0,
    monthlyChats:    raw.monthly_chats    ?? [],
    activeChatters:  raw.active_chatters  ?? [],
  }
}

export interface AdminUser {
  id: number
  username: string
  email: string
  role: string
  avatar?: string
  bio?: string
  created_at: string
  comment_count: number
}

export interface AdminUserUpdate {
  username?: string
  email?: string
  role?: string
  bio?: string
}

export interface AdminComment {
  id: number
  post_slug: string
  content: string
  created_at: string
  user_id: number
  username: string
  avatar?: string
  role: string
}

export interface ChatUserStat {
  user_id: number
  username: string
  avatar?: string
  role: string
  message_count: number
  last_at: string
}

export interface ChatMsgRecord {
  id: number
  role: string
  content: string
  created_at: string
}

export const adminApi = {
  stats: () => api.get<any>('/api/admin/stats').then(adapt),

  listUsers: (): Promise<AdminUser[]> =>
    api.get('/api/admin/users'),

  editUser: (id: number, data: AdminUserUpdate): Promise<{ message: string }> =>
    api.patch(`/api/admin/users/${id}`, data),

  deleteUser: (id: number): Promise<void> =>
    api.delete(`/api/admin/users/${id}`),

  listComments: (userId?: number): Promise<AdminComment[]> => {
    const url = userId != null ? `/api/admin/comments?user_id=${userId}` : '/api/admin/comments'
    return api.get(url)
  },

  deleteComment: (id: number): Promise<void> =>
    api.delete(`/api/comments/admin/${id}`),

  listChatUsers: (): Promise<ChatUserStat[]> =>
    api.get('/api/admin/chat'),

  getUserChat: (userId: number): Promise<ChatMsgRecord[]> =>
    api.get(`/api/admin/chat/${userId}`),

  clearUserChat: (userId: number): Promise<void> =>
    api.delete(`/api/admin/chat/${userId}`),
}
