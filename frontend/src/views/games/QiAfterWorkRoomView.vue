<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'
import { assetUrl } from '@/utils/assets'
import RoomScene from './qi-after-work/components/RoomScene.vue'
import RoomToolPanel from './qi-after-work/components/RoomToolPanel.vue'
import { roomAssets, roomNavigation, type RoomTool } from './qi-after-work/data/room'
import { useRoomGame } from './qi-after-work/composables/useRoomGame'

const router = useRouter()
const userStore = useUserStore()
const { profile, isLoggedIn } = storeToRefs(userStore)
const userId = computed(() => profile.value?.id)
const game = useRoomGame({ userId, isLoggedIn })
const { spots, selectedSpotId, selectedSpot, lastResult, loading, stateNotice, activeTool, character, state, selectSpot, walkToFloor, runAction, askFromRoom, runMoodAction, toggleTool, closeTool, updateFurniture } = game
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

function navigationAsset(name: string, isReturn = false) {
  return assetUrl(isReturn ? roomAssets.collectible(name) : roomAssets.ui(name))
}
</script>

<template>
  <div class="after-work-page">
    <header class="game-header">
      <nav class="room-navigation" aria-label="游戏导航">
        <button class="room-nav-button room-nav-button--return" type="button" title="返回游戏区" aria-label="返回游戏区" @click="router.push('/games')"><img :src="navigationAsset('backpack', true)" alt="" /></button>
        <button v-for="item in roomNavigation" :key="item.tool" class="room-nav-button" :class="{ active: activeTool === item.tool }" type="button" :title="item.label" :aria-label="item.label" @click="openTool(item.tool)"><img :src="navigationAsset(item.icon)" alt="" /></button>
      </nav>
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
:global(body.qi-after-work-active),:global(body.qi-after-work-active #app),:global(body.qi-after-work-active main) { height:100dvh; overflow:hidden; }.after-work-page { position:relative; width:100%; height:100dvh; overflow:hidden; background:#ecbd7c; color:#5c422b; isolation:isolate; }.game-header { position:absolute; z-index:12; top:max(14px,env(safe-area-inset-top)); right:16px; display:flex; pointer-events:none; }.room-shell { position:absolute; inset:0; z-index:0; }.room-navigation { display:flex; align-items:center; gap:7px; padding:7px; border:1px solid rgba(255,249,234,.6); border-radius:8px; background:rgba(255,250,240,.82); box-shadow:0 7px 20px rgba(84,54,29,.17); backdrop-filter:blur(8px); pointer-events:auto; }.room-nav-button { display:grid; width:60px; height:60px; place-items:center; padding:5px; border:1px solid transparent; border-radius:6px; background:transparent; cursor:pointer; }.room-nav-button img { display:block; width:100%; height:100%; object-fit:contain; filter:drop-shadow(0 3px 3px rgba(84,54,29,.12)); }.room-nav-button:hover,.room-nav-button:focus-visible,.room-nav-button.active { border-color:rgba(189,117,72,.42); background:#ffead0; outline:0; }.room-nav-button--return { margin-right:3px; border-right-color:rgba(152,104,61,.16); border-radius:6px 0 0 6px; }.tool-panel-enter-active,.tool-panel-leave-active { transition:opacity .2s ease,transform .2s ease; }.tool-panel-enter-from,.tool-panel-leave-to { opacity:0; transform:translateY(-6px); }@media (max-width:720px) { .game-header { top:max(9px,env(safe-area-inset-top)); right:10px; }.room-navigation { gap:3px; padding:4px; }.room-nav-button { width:42px; height:42px; padding:4px; } }
.state-notice { position:absolute; z-index:13; top:75px; right:22px; padding:9px 13px; border:1px solid rgba(152,104,61,.2); border-radius:6px; background:rgba(255,250,240,.95); box-shadow:0 7px 18px rgba(84,54,29,.18); color:#8a5d3d; font-size:12px; }.state-notice-enter-active,.state-notice-leave-active { transition:opacity .2s ease,transform .2s ease; }.state-notice-enter-from,.state-notice-leave-to { opacity:0; transform:translateY(-6px); }
</style>
