import { api } from './client'
import type { Project } from '@/types'

function adapt(raw: any): Project {
  return {
    id:          raw.id,
    name:        raw.name,
    description: raw.description,
    techStack:   raw.tech_stack ? raw.tech_stack.split(',').map((t: string) => t.trim()).filter(Boolean) : [],
    category:    raw.category,
    featured:    raw.featured ?? false,
    status:      raw.status ?? 'active',
    link:        raw.url,
    githubUrl:   raw.github,
    cover:       raw.cover,
  }
}

type ProjectPayload = {
  project_id?: string
  name: string
  description: string
  tech_stack: string
  category: string
  featured?: boolean
  status?: string
  github?: string
  url?: string
  cover?: string
}

export const projectsApi = {
  list(category?: string): Promise<Project[]> {
    const q = category ? `?category=${encodeURIComponent(category)}` : ''
    return api.get<any[]>(`/api/projects${q}`).then(r => r.map(adapt))
  },

  create(data: ProjectPayload): Promise<Project> {
    return api.post<any>('/api/projects', data).then(adapt)
  },

  update(id: number, data: Partial<ProjectPayload>): Promise<Project> {
    return api.patch<any>(`/api/projects/${id}`, data).then(adapt)
  },

  delete(id: number): Promise<void> {
    return api.delete(`/api/projects/${id}`)
  },
}
