export interface Post {
  slug: string
  title: string
  summary: string
  content: string
  tags: string[]
  createdAt: string
  readingTime: number
  viewCount: number
  cover?: string
}

export interface Project {
  id: number
  projectId?: string
  name: string
  description: string
  techStack: string[]
  category: string
  featured: boolean
  status: 'active' | 'completed' | 'archived'
  link?: string
  githubUrl?: string
  download?: string
  cover?: string
  highlights?: string[]
}

export interface Photo {
  id: number
  url: string
  alt: string
  tag: string
  sortOrder: number
  createdAt: string
}

export type MascotState = 'wave' | 'type' | 'think' | 'wind' | 'singing' | 'wake'
export type MascotSize = 'small' | 'medium' | 'large'
