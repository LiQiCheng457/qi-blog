import { computed, onUnmounted, ref, type Ref } from 'vue'
import type { RoomSpotId } from '@/api/room'
import { roomApi } from '@/api/room'
import { actionOutcomes, spots, statusItemLabels, statusLabels, type MoodAction, type RoomAction, type RoomTool } from '../data/room'
import { useRoomCharacter } from './useRoomCharacter'
import { useRoomState } from './useRoomState'

export function useRoomGame(options: { userId: Readonly<Ref<string | number | undefined>>; isLoggedIn: Readonly<Ref<boolean>> }) {
  const selectedSpotId = ref<RoomSpotId | null>(null)
  const lastResult = ref('')
  const loading = ref(false)
  const stateNotice = ref('')
  const menuOpen = ref(false)
  const activeTool = ref<RoomTool | null>(null)
  const character = useRoomCharacter()
  const state = useRoomState(options.userId)
  let resultTimer: ReturnType<typeof window.setTimeout> | undefined
  let stateNoticeTimer: ReturnType<typeof window.setTimeout> | undefined

  const selectedSpot = computed(() => spots.find((spot) => spot.id === selectedSpotId.value) ?? null)

  function dismissResult(after: number) {
    if (resultTimer) window.clearTimeout(resultTimer)
    resultTimer = window.setTimeout(() => { lastResult.value = '' }, after)
  }

  function updateFurniture(id: string, nextState: string) {
    state.updateFurniture(id, nextState)
    stateNotice.value = `${statusItemLabels[id] ?? id}：${statusLabels[nextState] ?? nextState}`
    if (stateNoticeTimer) window.clearTimeout(stateNoticeTimer)
    stateNoticeTimer = window.setTimeout(() => { stateNotice.value = '' }, 2600)
  }

  function selectSpot(id: RoomSpotId) {
    const spot = spots.find((item) => item.id === id)
    if (!spot) return
    selectedSpotId.value = null
    lastResult.value = ''
    character.moveTo(spot.arrivalX, spot.arrivalY, () => {
      selectedSpotId.value = id
      character.showEmote(id)
    })
  }

  function walkToFloor(event: MouseEvent) {
    if ((event.target as HTMLElement).closest('.room-hotspot, .action-panel, .room-menu, .room-tool-panel, .game-header')) return
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    const x = Math.max(7, Math.min(93, ((event.clientX - rect.left) / rect.width) * 100))
    const y = Math.max(67, Math.min(91, ((event.clientY - rect.top) / rect.height) * 100))
    selectedSpotId.value = null
    lastResult.value = ''
    character.moveTo(x, y)
  }

  async function askQi(spotId: RoomSpotId, actionId?: string, message = '') {
    if (!options.isLoggedIn.value) {
      lastResult.value = '水獭祁歪了歪头：先登录，再慢慢聊吧。'
      return
    }
    loading.value = true
    lastResult.value = '…'
    character.showEmote(spotId)
    try {
      let receivedFirstChunk = false
      await roomApi.chatStream({ spotId, actionId, message }, (chunk) => {
        if (!receivedFirstChunk) { lastResult.value = ''; receivedFirstChunk = true }
        lastResult.value += chunk
      })
    } catch (error) {
      lastResult.value = error instanceof Error ? error.message : '水獭祁现在没有接上信号，请稍后再试。'
    } finally {
      loading.value = false
    }
  }

  async function runAction(action: RoomAction) {
    const spot = selectedSpot.value
    if (!spot) return
    lastResult.value = action.result
    const outcome = actionOutcomes[action.id]
    if (outcome?.furniture) updateFurniture(...outcome.furniture)
    if (outcome?.collectible) state.unlockItem(outcome.collectible)
    if (outcome?.emote) character.showEmote(spot.id, outcome.emote)
    if (outcome?.effect) character.showEffect(outcome.effect)
    state.addMemory(spot.name, action.label)
    state.unlockAchievement('first-action')
    state.save()
    selectedSpotId.value = null
    await askQi(spot.id, action.id)
    dismissResult(5200)
  }

  async function askFromRoom(message: string) {
    const spot = selectedSpot.value
    if (!spot || loading.value) return
    selectedSpotId.value = null
    await askQi(spot.id, undefined, message)
    dismissResult(7200)
  }

  async function runMoodAction(action: MoodAction) {
    activeTool.value = null
    menuOpen.value = false
    character.showEmote(action.spotId, action.emote)
    character.showEffect(action.effect)
    state.addMemory('和水獭祁聊了聊', action.label)
    state.unlockAchievement('first-action')
    state.save()
    await askQi(action.spotId, undefined, action.message)
    dismissResult(7200)
  }

  function toggleTool(tool: RoomTool) {
    activeTool.value = activeTool.value === tool ? null : tool
    menuOpen.value = true
  }

  function closeTool() { activeTool.value = null; menuOpen.value = false }

  onUnmounted(() => {
    if (resultTimer) window.clearTimeout(resultTimer)
    if (stateNoticeTimer) window.clearTimeout(stateNoticeTimer)
  })

  return { spots, selectedSpotId, selectedSpot, lastResult, loading, stateNotice, menuOpen, activeTool, character, state, selectSpot, walkToFloor, runAction, askFromRoom, runMoodAction, toggleTool, closeTool, updateFurniture }
}
