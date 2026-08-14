<script setup lang="ts">
import { computed } from 'vue'
import { assetUrl } from '@/utils/assets'
import { roomAssets, roomSceneObjects, roomStatusLabels, spotDefaultStates, statusLabels, type RoomAction, type RoomSceneObject, type RoomSpot } from '../data/room'
import RoomActionPanel from './RoomActionPanel.vue'

defineProps<{
  spots: RoomSpot[]
  selectedSpot: RoomSpot | null
  selectedSpotId: string | null
  lastResult: string
  loading: boolean
  position: { x: number; y: number }
  moving: boolean
  facingLeft: boolean
  activeEmote: string | null
  activeEffect: string | null
  bubbleOnLeft: boolean
  bubbleStyle: Record<string, string>
  furnitureStates: Record<string, string>
}>()
const emit = defineEmits<{ floor: [event: MouseEvent]; select: [id: RoomSpot['id']]; close: []; action: [action: RoomAction]; question: [message: string] }>()
const visibleSceneObjects = computed(() => roomSceneObjects.filter((object) => object.visible !== false))

function statusState(spot: RoomSpot, furnitureStates: Record<string, string>) {
  return furnitureStates[spot.id] ?? spotDefaultStates[spot.id]
}

function statusLabel(spot: RoomSpot, furnitureStates: Record<string, string>) {
  const state = statusState(spot, furnitureStates)
  return roomStatusLabels[state] ?? '一切如常'
}

function statusBubbleStyle(spot: RoomSpot) {
  return {
    left: `${Math.max(10, Math.min(90, spot.x + spot.width / 2))}%`,
    top: `${Math.max(12, spot.y + 3)}%`,
  }
}

function objectAsset(object: RoomSceneObject, furnitureStates: Record<string, string>) {
  const state = furnitureStates[object.stateId] ?? `${object.id}-${object.defaultState}`
  const stateName = state.slice(object.id.length + 1)
  return assetUrl(roomAssets.object(object.id, stateName))
}
</script>

<template>
  <div class="room-stage" @click="emit('floor', $event)">
    <img :src="assetUrl(roomAssets.room)" class="room-image" alt="水獭祁的房间" draggable="false" /><div class="sun-wash"></div>
    <img v-for="object in visibleSceneObjects" :key="object.id" class="room-object" :src="objectAsset(object, furnitureStates)" alt="" aria-hidden="true" draggable="false" :style="{ left: `${object.x}%`, bottom: `${object.floor}%`, width: `${object.width}%`, zIndex: object.z, '--offset-x': `${object.offsetX ?? 0}%`, '--offset-y': `${object.offsetY ?? 0}%` }" />
    <div class="qi-character" :class="{ moving, 'facing-left': facingLeft }" :style="{ left: `${position.x}%`, top: `${position.y}%` }" aria-label="水獭祁"><img :src="assetUrl(roomAssets.qiIdle)" alt="水獭祁" draggable="false" /><span v-if="moving">走走…</span></div>
    <Transition name="qi-emote"><img v-if="activeEmote && !selectedSpot" class="qi-emote" :src="activeEmote" alt="" aria-hidden="true" :style="{ left: `${position.x}%`, top: `calc(${position.y}% - clamp(100px, 11vw, 180px))` }" /></Transition>
    <Transition name="room-effect"><img v-if="activeEffect" :src="activeEffect" class="room-effect" alt="" aria-hidden="true" :style="{ left: `${position.x}%`, top: `calc(${position.y}% - clamp(150px, 16vw, 250px))` }" /></Transition>
    <Transition name="qi-bubble"><aside v-if="lastResult && !selectedSpot" class="qi-dialogue" :class="{ 'qi-dialogue--left': bubbleOnLeft }" :style="bubbleStyle" aria-live="polite"><p>{{ lastResult }}</p></aside></Transition>
    <button v-for="spot in spots" :key="spot.id" class="room-hotspot" :class="{ selected: selectedSpotId === spot.id }" :style="{ left: `${spot.x}%`, top: `${spot.y}%`, width: `${spot.width}%`, height: `${spot.height}%` }" type="button" @click="emit('select', spot.id)"><span>{{ spot.name }}</span><small>{{ spot.hint }}</small></button>
    <Transition name="room-status"><aside v-if="selectedSpot" class="room-status-bubble" :class="{ 'room-status-bubble--with-image': statusLabels[statusState(selectedSpot, furnitureStates)] }" :style="statusBubbleStyle(selectedSpot)" aria-live="polite"><img v-if="statusLabels[statusState(selectedSpot, furnitureStates)]" :src="assetUrl(roomAssets.prop(statusState(selectedSpot, furnitureStates)))" :alt="`${selectedSpot.name}${statusLabel(selectedSpot, furnitureStates)}`" /><div><span>{{ selectedSpot.name }}</span><strong>{{ statusLabel(selectedSpot, furnitureStates) }}</strong></div></aside></Transition>
    <Transition name="action-panel"><RoomActionPanel v-if="selectedSpot" :spot="selectedSpot" :loading="loading" @close="emit('close')" @action="emit('action', $event)" @question="emit('question', $event)" /></Transition>
    <slot />
  </div>
</template>

<style scoped>
.room-stage { position:relative; width:100%; height:100%; overflow:hidden; background:#f4ddb9; isolation:isolate; }.room-image { display:block; width:100%; height:100%; object-fit:cover; object-position:center; user-select:none; }.sun-wash { position:absolute; inset:0; z-index:1; pointer-events:none; background:rgba(255,240,196,.03); }.room-object { position:absolute; display:block; height:auto; transform:translate(calc(-50% + var(--offset-x)),var(--offset-y)); pointer-events:none; user-select:none; filter:drop-shadow(0 5px 4px rgba(83,55,26,.12)); }.qi-character { position:absolute; z-index:5; width:clamp(80px,7vw,135px); transform:translate(-50%,-100%); transition:left 1.35s cubic-bezier(.22,.78,.32,1),top 1.35s cubic-bezier(.22,.78,.32,1); pointer-events:none; filter:drop-shadow(0 6px 6px rgba(83,55,26,.2)); }.qi-character img { display:block; width:100%; animation:qi-idle 2.6s ease-in-out infinite; transform-origin:center bottom; }.qi-character.facing-left img { transform:scaleX(-1); }.qi-character.moving img { animation:qi-walk .42s ease-in-out infinite alternate; }.qi-character span { position:absolute; top:-10px; left:50%; padding:2px 6px; transform:translateX(-50%); border-radius:4px; background:rgba(255,250,240,.86); color:#806046; font-size:10px; white-space:nowrap; }.qi-emote,.room-effect { position:absolute; z-index:6; transform:translate(-50%,-100%); pointer-events:none; filter:drop-shadow(0 5px 6px rgba(83,55,26,.13)); }.qi-emote { width:clamp(72px,8vw,125px); }.room-effect { width:clamp(84px,11vw,170px); }.room-hotspot { position:absolute; z-index:7; display:flex; flex-direction:column; align-items:center; justify-content:center; border:0; outline:0; background:transparent; color:#6b4630; cursor:pointer; }.room-hotspot span,.room-hotspot small { opacity:0; pointer-events:none; transition:opacity .16s ease,transform .16s ease; }.room-hotspot span { padding:2px 7px; border-radius:4px; background:rgba(255,251,241,.94); box-shadow:0 2px 8px rgba(92,58,29,.12); font-size:12px; font-weight:700; transform:translateY(3px); }.room-hotspot small { margin-top:3px; font-size:10px; color:#8a684d; }.room-hotspot:hover span,.room-hotspot:hover small,.room-hotspot:focus-visible span,.room-hotspot:focus-visible small { opacity:1; }.room-hotspot:hover span,.room-hotspot:focus-visible span { transform:translateY(0); }.room-hotspot:focus-visible { box-shadow:inset 0 0 0 2px rgba(255,250,235,.86); border-radius:4px; }.qi-dialogue { position:absolute; z-index:8; width:fit-content; max-width:min(310px,34vw); margin-left:clamp(26px,3vw,48px); padding:12px 14px; border:1px solid rgba(152,104,61,.25); border-radius:7px; background:rgba(255,250,240,.94); box-shadow:0 8px 22px rgba(85,52,25,.16); color:#6f4e36; font-size:13px; line-height:1.65; backdrop-filter:blur(7px); pointer-events:none; }.qi-dialogue--left { margin:0 clamp(26px,3vw,48px) 0 0; transform:translateX(-100%); }.qi-dialogue p { margin:0; }.qi-bubble-enter-active,.qi-bubble-leave-active,.action-panel-enter-active,.action-panel-leave-active,.qi-emote-enter-active,.qi-emote-leave-active,.room-effect-enter-active,.room-effect-leave-active { transition:opacity .22s ease,transform .22s ease; }.qi-bubble-enter-from,.qi-bubble-leave-to,.action-panel-enter-from,.action-panel-leave-to { opacity:0; transform:translateY(8px); }.qi-emote-enter-from,.qi-emote-leave-to { opacity:0; transform:translate(-50%,-100%) scale(.72) rotate(-8deg); }.room-effect-enter-from,.room-effect-leave-to { opacity:0; transform:translate(-50%,-85%) scale(.78); }@keyframes qi-idle { 50% { translate:0 -3px; } }@keyframes qi-walk { from { translate:0 0; rotate:-2deg; } to { translate:0 -5px; rotate:2deg; } }@media (max-width:720px) { .qi-dialogue { width:min(245px,61vw); margin-left:18px; padding:10px 11px; font-size:12px; }.qi-dialogue--left { margin-right:18px; }.room-hotspot span { font-size:10px; padding:1px 4px; }.room-hotspot small { display:none; } }
.room-status-bubble { position:absolute; z-index:5; display:grid; gap:2px; min-width:88px; padding:7px 9px; transform:translate(-50%,-100%); border:1px solid rgba(152,104,61,.23); border-radius:6px; background:rgba(255,250,240,.94); box-shadow:0 6px 16px rgba(84,54,29,.16); color:#805438; pointer-events:none; }.room-status-bubble--with-image { grid-template-columns:54px minmax(72px,1fr); align-items:center; gap:7px; min-width:150px; }.room-status-bubble img { display:block; width:54px; height:44px; object-fit:contain; }.room-status-bubble div { display:grid; gap:2px; }.room-status-bubble::after { content:''; position:absolute; bottom:-6px; left:50%; width:10px; height:10px; border-right:1px solid rgba(152,104,61,.23); border-bottom:1px solid rgba(152,104,61,.23); background:rgba(255,250,240,.94); transform:translateX(-50%) rotate(45deg); }.room-status-bubble span { color:#aa7b58; font-size:10px; }.room-status-bubble strong { font-size:12px; font-weight:600; }.room-status-enter-active,.room-status-leave-active { transition:opacity .2s ease,transform .2s ease; }.room-status-enter-from,.room-status-leave-to { opacity:0; transform:translate(-50%,-88%) scale(.86); }
</style>
