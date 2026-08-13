import { computed, ref, watch, type Ref } from 'vue'
import { collectibleItems } from '../data/room'

export type RoomMemory = { id: string; title: string; detail: string; createdAt: string }

type StoredRoomState = {
  furnitureStates?: Record<string, string>
  discoveredItems?: string[]
  memories?: RoomMemory[]
  achievements?: string[]
}

export function useRoomState(userId: Readonly<Ref<string | number | undefined>>) {
  const furnitureStates = ref<Record<string, string>>({})
  const discoveredItems = ref<string[]>([])
  const memories = ref<RoomMemory[]>([])
  const achievements = ref<string[]>([])
  const stateKey = computed(() => `qi-after-work-state:${userId.value ?? 'guest'}`)

  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(stateKey.value) ?? '{}') as StoredRoomState
      furnitureStates.value = saved.furnitureStates ?? {}
      discoveredItems.value = saved.discoveredItems ?? []
      memories.value = saved.memories ?? []
      achievements.value = saved.achievements ?? []
    } catch {
      furnitureStates.value = {}
      discoveredItems.value = []
      memories.value = []
      achievements.value = []
    }
  }

  function save() {
    localStorage.setItem(stateKey.value, JSON.stringify({
      furnitureStates: furnitureStates.value,
      discoveredItems: discoveredItems.value,
      memories: memories.value.slice(0, 30),
      achievements: achievements.value,
    }))
  }

  function unlockAchievement(id: string) {
    if (!achievements.value.includes(id)) achievements.value.push(id)
  }

  function unlockItem(id: string) {
    if (!discoveredItems.value.includes(id)) discoveredItems.value.push(id)
    if (discoveredItems.value.length === collectibleItems.length) unlockAchievement('all-collectibles')
    if (discoveredItems.value.length >= 5) unlockAchievement('five-collectibles')
  }

  function updateFurniture(id: string, state: string) {
    furnitureStates.value[id] = state
    save()
  }

  function addMemory(title: string, detail: string) {
    memories.value.unshift({
      id: `${Date.now()}-${Math.random()}`,
      title,
      detail,
      createdAt: new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
    })
    memories.value = memories.value.slice(0, 30)
    unlockAchievement('first-memory')
    save()
  }

  watch(userId, load)

  return { furnitureStates, discoveredItems, memories, achievements, load, save, unlockAchievement, unlockItem, updateFurniture, addMemory }
}
