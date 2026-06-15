import { api } from './client'

export interface ExeFile {
  filename: string
  url: string
  size: number
}

export const exesApi = {
  list(): Promise<ExeFile[]> {
    return api.get<ExeFile[]>('/api/admin/exes')
  },

  upload(file: File): Promise<ExeFile> {
    const fd = new FormData()
    fd.append('file', file)
    return api.postForm<ExeFile>('/api/admin/exes', fd)
  },

  delete(filename: string): Promise<void> {
    return api.delete(`/api/admin/exes/${encodeURIComponent(filename)}`)
  },
}
