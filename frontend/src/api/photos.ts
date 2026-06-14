import { api } from './client'
import type { Photo } from '@/types'

function adapt(raw: any): Photo {
  return {
    id:        raw.id,
    url:       raw.url,
    alt:       raw.alt,
    tag:       raw.tag,
    sortOrder: raw.sort_order,
    createdAt: raw.created_at,
  }
}

export const photosApi = {
  list(tag?: string): Promise<Photo[]> {
    const q = tag ? `?tag=${encodeURIComponent(tag)}` : ''
    return api.get<any[]>(`/api/photos${q}`).then(r => r.map(adapt))
  },

  upload(file: File, alt: string, tag: string): Promise<Photo> {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('alt', alt)
    fd.append('tag', tag)
    return api.postForm<any>('/api/photos', fd).then(adapt)
  },

  update(id: number, data: { alt?: string; tag?: string; sort_order?: number }): Promise<Photo> {
    return api.patch<any>(`/api/photos/${id}`, data).then(adapt)
  },

  delete(id: number): Promise<void> {
    return api.delete(`/api/photos/${id}`)
  },
}
