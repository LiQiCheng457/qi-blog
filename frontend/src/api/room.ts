import { getToken } from './client'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export type RoomSpotId = 'window' | 'fridge' | 'sofa' | 'desk' | 'bookshelf' | 'bed' | 'door'

export const roomApi = {
  async chatStream(
    data: { spotId: RoomSpotId; actionId?: string; message?: string },
    onChunk: (chunk: string) => void,
  ) {
    const token = getToken()
    const response = await fetch(`${API_BASE}/api/room/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
      scene_id: 'after-work',
      spot_id: data.spotId,
      action_id: data.actionId,
      message: data.message ?? '',
      }),
    })

    if (!response.ok || !response.body) {
      const error = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(error.detail ?? '请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      onChunk(decoder.decode(value, { stream: true }))
    }
  },
}
