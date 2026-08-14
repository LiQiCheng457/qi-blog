<script setup lang="ts">
import { computed } from 'vue'
import { assetUrl } from '@/utils/assets'
import { achievementItems, collectibleItems, moodActions, roomAssets, statusItems, statusLabels, type RoomTool } from '../data/room'
import type { RoomMemory } from '../composables/useRoomState'

const props = defineProps<{ activeTool: RoomTool; furnitureStates: Record<string, string>; discoveredItems: string[]; memories: RoomMemory[]; achievements: string[]; loading: boolean }>()
const emit = defineEmits<{ close: []; 'update-furniture': [id: string, state: string]; 'mood-action': [action: typeof moodActions[number]] }>()
const title = computed(() => ({ status: '房间状态', collection: '收藏图鉴', memory: '今日记忆', emotions: '情绪互动', achievements: '成就' })[props.activeTool])
const propAsset = (name: string) => assetUrl(roomAssets.prop(name))
const collectibleAsset = (name: string) => assetUrl(roomAssets.collectible(name))
</script>

<template>
  <aside class="room-tool-panel" aria-live="polite">
    <div class="tool-heading"><h2>{{ title }}</h2><button type="button" aria-label="关闭菜单" @click="emit('close')">×</button></div>
    <div v-if="activeTool === 'status'" class="status-grid">
      <article v-for="item in statusItems" :key="item.id" class="status-card">
        <img :src="propAsset(furnitureStates[item.id] ?? item.states[0])" :alt="item.label" />
        <div><strong>{{ item.label }}</strong><small>当前：{{ statusLabels[furnitureStates[item.id] ?? item.states[0]] }}</small></div>
        <div class="state-options"><button v-for="(state, index) in item.states" :key="state" type="button" :class="{ active: (furnitureStates[item.id] ?? item.states[0]) === state }" :title="item.stateLabels[index]" @click="emit('update-furniture', item.id, state)"></button></div>
      </article>
    </div>
    <div v-else-if="activeTool === 'collection'">
      <p class="collection-progress">已收集 {{ discoveredItems.length }} / {{ collectibleItems.length }}</p>
      <div class="collection-grid"><article v-for="item in collectibleItems" :key="item[0]" class="collection-item" :class="{ locked: !discoveredItems.includes(item[0]) }"><img :src="collectibleAsset(item[0])" :alt="discoveredItems.includes(item[0]) ? item[1] : '未知收藏'" /><span>{{ discoveredItems.includes(item[0]) ? item[1] : '未知收藏' }}</span></article></div>
    </div>
    <div v-else-if="activeTool === 'memory'" class="memory-list"><p v-if="!memories.length" class="tool-empty">房间还没有新记忆。</p><article v-for="memory in memories" :key="memory.id" class="memory-item"><time>{{ memory.createdAt }}</time><strong>{{ memory.title }}</strong><p>{{ memory.detail }}</p></article></div>
    <div v-else-if="activeTool === 'emotions'" class="mood-grid"><button v-for="action in moodActions" :key="action.id" class="mood-button" type="button" :disabled="loading" @click="emit('mood-action', action)">{{ action.label }}</button></div>
    <div v-else class="achievement-list"><article v-for="achievement in achievementItems" :key="achievement.id" class="achievement-item" :class="{ locked: !achievements.includes(achievement.id) }"><img :src="collectibleAsset(achievement.icon)" alt="" /><div><strong>{{ achievement.title }}</strong><span>{{ achievement.detail }}</span></div></article></div>
  </aside>
</template>

<style scoped>
.room-tool-panel { position:absolute; z-index:11; top:98px; right:20px; width:min(370px,calc(100% - 40px)); max-height:calc(100% - 120px); overflow:auto; padding:14px; border:1px solid rgba(255,249,234,.62); border-radius:7px; background:rgba(255,250,240,.96); box-shadow:0 15px 36px rgba(84,54,29,.23); backdrop-filter:blur(11px); }.tool-heading { display:flex; align-items:center; justify-content:space-between; margin-bottom:11px; border-bottom:1px solid rgba(152,104,61,.14); padding-bottom:9px; }.tool-heading h2 { margin:0; color:#65452f; font:600 18px/1.2 'Noto Serif SC',serif; }.tool-heading button { display:grid; width:27px; height:27px; place-items:center; border:0; border-radius:4px; background:transparent; color:#987252; font-size:22px; cursor:pointer; }.tool-heading button:hover { background:#ffead0; }.status-grid,.memory-list,.achievement-list { display:grid; gap:8px; }.status-card { display:grid; grid-template-columns:64px 1fr; align-items:center; gap:9px; padding:7px; border-bottom:1px solid rgba(152,104,61,.12); }.status-card img { width:64px; height:49px; object-fit:contain; }.status-card strong,.status-card small { display:block; }.status-card strong,.achievement-item strong { font-size:13px; }.status-card small,.achievement-item span { margin-top:2px; color:#987456; font-size:11px; }.state-options { grid-column:1 / -1; display:flex; gap:5px; }.state-options button { width:20px; height:5px; border:0; border-radius:3px; background:#e6c2a1; cursor:pointer; }.state-options button.active,.state-options button:hover { background:#bc7547; }.collection-progress { margin:0 0 10px; color:#8a6044; font-size:12px; }.collection-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:7px; }.collection-item { min-width:0; padding:5px 3px; border:1px solid rgba(152,104,61,.13); border-radius:5px; text-align:center; }.collection-item img { display:block; width:100%; height:52px; object-fit:contain; }.collection-item span { display:block; overflow:hidden; margin-top:3px; color:#744f37; font-size:10px; text-overflow:ellipsis; white-space:nowrap; }.collection-item.locked img { filter:grayscale(1) brightness(.52); }.collection-item.locked span { color:#a98b74; }.tool-empty { margin:4px 0; color:#9a755a; font-size:12px; }.memory-item { padding:9px; border-left:3px solid #d69b6d; background:#fff6e8; }.memory-item time { display:block; margin-bottom:2px; color:#a77a5b; font-size:10px; }.memory-item strong { color:#674630; font-size:13px; }.memory-item p { margin:3px 0 0; color:#8e694f; font-size:12px; }.mood-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:8px; }.mood-button { min-height:52px; border:1px solid rgba(152,104,61,.18); border-radius:5px; background:#fff6e8; color:#694a34; font:13px inherit; cursor:pointer; }.mood-button:hover { background:#ffead0; border-color:rgba(178,108,58,.45); }.mood-button:disabled { opacity:.55; cursor:default; }.achievement-item { display:flex; align-items:center; gap:10px; padding:8px; border:1px solid rgba(152,104,61,.13); border-radius:5px; }.achievement-item img { width:42px; height:42px; object-fit:contain; }.achievement-item strong,.achievement-item span { display:block; }.achievement-item strong { color:#694a34; }.achievement-item.locked { opacity:.52; filter:grayscale(1); }@media (max-width:720px) { .room-tool-panel { top:66px; right:10px; width:calc(100% - 20px); max-height:calc(100% - 84px); } }
</style>
