<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'
import RoomScene from './qi-after-work/components/RoomScene.vue'
import RoomToolPanel from './qi-after-work/components/RoomToolPanel.vue'
import { type RoomTool } from './qi-after-work/data/room'
import { useRoomGame } from './qi-after-work/composables/useRoomGame'

const roomTools: RoomTool[] = ['status', 'collection', 'memory', 'emotions', 'achievements']
const toolLabels: Record<RoomTool, string> = {
  status: '房间状态',
  collection: '收藏图鉴',
  memory: '今日记忆',
  emotions: '情绪互动',
  achievements: '成就',
}

const router = useRouter()
const userStore = useUserStore()
const { profile, isLoggedIn } = storeToRefs(userStore)
const userId = computed(() => profile.value?.id)
const game = useRoomGame({ userId, isLoggedIn })
const { spots, selectedSpotId, selectedSpot, lastResult, loading, stateNotice, menuOpen, activeTool, character, state, selectSpot, walkToFloor, runAction, askFromRoom, runMoodAction, toggleTool, closeTool, updateFurniture } = game
const { position, moving, facingLeft, activeEmote, activeEffect, bubbleOnLeft, bubbleStyle } = character
const { furnitureStates, discoveredItems, memories, achievements } = state

onMounted(() => {
  document.body.classList.add('qi-after-work-active')
  state.load()
})

onUnmounted(() => document.body.classList.remove('qi-after-work-active'))

function openTool(tool: RoomTool) {
  toggleTool(tool)
}
</script>

<template>
  <div class="after-work-page">
    <header class="game-header">
      <button class="icon-button" type="button" title="返回游戏区" aria-label="返回游戏区" @click="router.push('/games')">←</button>
      <div class="room-tools">
        <button class="icon-button" type="button" title="房间菜单" aria-label="房间菜单" @click="menuOpen = !menuOpen">☰</button>
        <aside v-if="menuOpen" class="room-menu" aria-label="房间功能菜单">
          <button v-for="tool in roomTools" :key="tool" type="button" :class="{ active: activeTool === tool }" @click="openTool(tool)">{{ toolLabels[tool] }}</button>
        </aside>
      </div>
    </header>
    <main class="room-shell">
      <RoomScene
        :spots="spots"
        :selected-spot="selectedSpot"
        :selected-spot-id="selectedSpotId"
        :last-result="lastResult"
        :loading="loading"
        :position="position"
        :moving="moving"
        :facing-left="facingLeft"
        :active-emote="activeEmote"
        :active-effect="activeEffect"
        :bubble-on-left="bubbleOnLeft"
        :bubble-style="bubbleStyle"
        :furniture-states="furnitureStates"
        @floor="walkToFloor"
        @select="selectSpot"
        @close="selectedSpotId = null"
        @action="runAction"
        @question="askFromRoom"
      >
        <Transition name="tool-panel"><RoomToolPanel v-if="activeTool" :active-tool="activeTool" :furniture-states="furnitureStates" :discovered-items="discoveredItems" :memories="memories" :achievements="achievements" :loading="loading" @close="closeTool" @update-furniture="updateFurniture" @mood-action="runMoodAction" /></Transition>
        <Transition name="state-notice"><div v-if="stateNotice" class="state-notice">{{ stateNotice }}</div></Transition>
      </RoomScene>
    </main>
  </div>
</template>

<style scoped>
:global(body.qi-after-work-active),:global(body.qi-after-work-active #app),:global(body.qi-after-work-active main) { height:100dvh; overflow:hidden; }.after-work-page { position:relative; width:100%; height:100dvh; overflow:hidden; background:#ecbd7c; color:#5c422b; isolation:isolate; }.game-header { position:absolute; z-index:5; top:max(14px,env(safe-area-inset-top)); left:16px; right:16px; display:flex; align-items:center; justify-content:space-between; pointer-events:none; }.room-shell { position:absolute; inset:0; z-index:0; }.icon-button { pointer-events:auto; display:grid; width:40px; height:40px; place-items:center; border:1px solid rgba(255,249,234,.54); border-radius:50%; background:rgba(97,65,36,.28); box-shadow:0 4px 14px rgba(86,52,24,.16); color:#fffaf0; font-size:23px; line-height:1; backdrop-filter:blur(7px); cursor:pointer; }.icon-button:hover { background:rgba(97,65,36,.45); }.room-tools { position:relative; pointer-events:auto; }.room-menu { position:absolute; top:48px; right:0; z-index:12; display:grid; width:126px; padding:5px; border:1px solid rgba(255,249,234,.62); border-radius:7px; background:rgba(255,250,240,.95); box-shadow:0 12px 28px rgba(84,54,29,.2); backdrop-filter:blur(10px); }.room-menu button { padding:8px 9px; border:0; border-radius:4px; background:transparent; color:#694a34; font:12px inherit; text-align:left; cursor:pointer; }.room-menu button:hover,.room-menu button.active { background:#ffead0; color:#9a5f39; }.tool-panel-enter-active,.tool-panel-leave-active { transition:opacity .2s ease,transform .2s ease; }.tool-panel-enter-from,.tool-panel-leave-to { opacity:0; transform:translateY(-6px); }@media (max-width:720px) { .game-header { top:max(9px,env(safe-area-inset-top)); left:10px; right:10px; }.icon-button { width:36px; height:36px; font-size:21px; } }
.state-notice { position:absolute; z-index:13; top:75px; right:22px; padding:9px 13px; border:1px solid rgba(152,104,61,.2); border-radius:6px; background:rgba(255,250,240,.95); box-shadow:0 7px 18px rgba(84,54,29,.18); color:#8a5d3d; font-size:12px; }.state-notice-enter-active,.state-notice-leave-active { transition:opacity .2s ease,transform .2s ease; }.state-notice-enter-from,.state-notice-leave-to { opacity:0; transform:translateY(-6px); }
</style>
