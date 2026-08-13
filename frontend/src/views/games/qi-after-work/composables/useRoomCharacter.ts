import { computed, onUnmounted, ref } from 'vue'
import type { RoomSpotId } from '@/api/room'
import { roomAssets, spotEmotes } from '../data/room'
import { assetUrl } from '@/utils/assets'

const effectImages: Record<string, string> = Object.fromEntries(
  ['rain', 'game-pixels', 'hearts', 'sparkles', 'sunbeam', 'question', 'sleep', 'surprised', 'sweat', 'thundercloud'].map((name) => [name === 'game-pixels' ? 'pixels' : name, assetUrl(roomAssets.effect(name))]),
)

export function useRoomCharacter() {
  const position = ref({ x: 50, y: 76 })
  const moving = ref(false)
  const facingLeft = ref(false)
  const activeEmote = ref<string | null>(null)
  const activeEffect = ref<string | null>(null)
  let moveTimer: ReturnType<typeof window.setTimeout> | undefined
  let emoteTimer: ReturnType<typeof window.setTimeout> | undefined
  let effectTimer: ReturnType<typeof window.setTimeout> | undefined

  const bubbleOnLeft = computed(() => position.value.x > 62)
  const bubbleStyle = computed(() => ({ left: `${position.value.x}%`, top: `calc(${position.value.y}% - clamp(150px, 16vw, 270px))` }))

  function showEmote(spotId: RoomSpotId, emote = spotEmotes[spotId]) {
    activeEmote.value = assetUrl(roomAssets.emote(emote))
    if (emoteTimer) window.clearTimeout(emoteTimer)
    emoteTimer = window.setTimeout(() => { activeEmote.value = null }, 3000)
  }

  function showEffect(name: string) {
    activeEffect.value = effectImages[name] ?? null
    if (effectTimer) window.clearTimeout(effectTimer)
    effectTimer = window.setTimeout(() => { activeEffect.value = null }, 2600)
  }

  function moveTo(x: number, y: number, onArrive?: () => void) {
    if (moveTimer) window.clearTimeout(moveTimer)
    const distance = Math.abs(x - position.value.x) + Math.abs(y - position.value.y)
    facingLeft.value = x < position.value.x
    moving.value = true
    position.value = { x, y }
    const duration = Math.min(2800, Math.max(900, distance * 65))
    moveTimer = window.setTimeout(() => { moving.value = false; onArrive?.() }, duration)
  }

  onUnmounted(() => {
    if (moveTimer) window.clearTimeout(moveTimer)
    if (emoteTimer) window.clearTimeout(emoteTimer)
    if (effectTimer) window.clearTimeout(effectTimer)
  })

  return { position, moving, facingLeft, activeEmote, activeEffect, bubbleOnLeft, bubbleStyle, showEmote, showEffect, moveTo }
}
