const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

const TOKEN_KEY = 'qi_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

async function request<T>(path: string, init: RequestInit = {}, skipContentType = false): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = skipContentType
    ? { ...(init.headers as Record<string, string>) }
    : { 'Content-Type': 'application/json', ...(init.headers as Record<string, string>) }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...init, headers })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? '请求失败')
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  get:      <T>(path: string)                  => request<T>(path, { method: 'GET' }),
  post:     <T>(path: string, body: unknown)   => request<T>(path, { method: 'POST',   body: JSON.stringify(body) }),
  patch:    <T>(path: string, body: unknown)   => request<T>(path, { method: 'PATCH',  body: JSON.stringify(body) }),
  delete:   <T>(path: string)                  => request<T>(path, { method: 'DELETE' }),
  postForm: <T>(path: string, body: FormData)  => request<T>(path, { method: 'POST',   body }, true),
}
