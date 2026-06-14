import { api } from './client'

export interface MonthStat { month: string; count: number }
export interface TopPost { title: string; views: number }

export interface DashboardStats {
  postCount: number
  pubCount: number
  viewTotal: number
  commentCount: number
  userCount: number
  monthlyPosts: MonthStat[]
  monthlyComments: MonthStat[]
  topPosts: TopPost[]
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
  }
}

export const adminApi = {
  stats: () => api.get<any>('/api/admin/stats').then(adapt),
}
