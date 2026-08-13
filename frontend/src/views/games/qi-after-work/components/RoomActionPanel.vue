<script setup lang="ts">
import { ref } from 'vue'
import type { RoomAction, RoomSpot } from '../data/room'

defineProps<{ spot: RoomSpot; loading: boolean }>()
const emit = defineEmits<{ close: []; action: [action: RoomAction]; question: [message: string] }>()
const question = ref('')

function submit() {
  const message = question.value.trim()
  if (!message) return
  question.value = ''
  emit('question', message)
}
</script>

<template>
  <aside class="action-panel" aria-live="polite">
    <div class="panel-heading"><div><span>{{ spot.hint }}</span><h2>{{ spot.name }}</h2></div><button type="button" aria-label="关闭" @click="emit('close')">×</button></div>
    <button v-for="action in spot.actions" :key="action.id" class="action-button" type="button" @click="emit('action', action)"><strong>{{ action.label }}</strong><span>{{ action.detail }}</span></button>
    <form class="room-question" @submit.prevent="submit"><input v-model="question" :disabled="loading" maxlength="200" placeholder="问问水獭祁…" aria-label="向水獭祁提问" /><button type="submit" :disabled="loading || !question.trim()">{{ loading ? '…' : '问' }}</button></form>
  </aside>
</template>

<style scoped>
.action-panel { position:absolute; z-index:6; right:20px; bottom:22px; width:min(330px,calc(100% - 40px)); padding:15px; border:1px solid rgba(255,249,234,.55); border-radius:7px; background:rgba(255,250,240,.94); box-shadow:0 15px 36px rgba(84,54,29,.23); backdrop-filter:blur(10px); }.panel-heading { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; }.panel-heading span { font-size:11px; color:#ab805c; }.panel-heading h2 { margin:1px 0 0; font:600 19px/1.2 'Noto Serif SC',serif; }.panel-heading button { border:0; background:transparent; color:#987252; font-size:21px; line-height:1; cursor:pointer; }.action-button { display:block; width:100%; margin-top:7px; padding:10px 11px; border:1px solid rgba(152,104,61,.18); border-radius:5px; background:#fff6e8; color:#684631; text-align:left; cursor:pointer; }.action-button:hover { background:#ffebd2; border-color:rgba(178,108,58,.45); }.action-button strong,.action-button span { display:block; }.action-button strong { font-size:13px; }.action-button span { margin-top:2px; font-size:11px; color:#987456; }.room-question { display:flex; gap:6px; margin-top:11px; padding-top:11px; border-top:1px solid rgba(152,104,61,.14); }.room-question input { min-width:0; flex:1; border:1px solid rgba(152,104,61,.25); border-radius:5px; outline:0; background:#fffdf7; color:#684631; padding:8px 9px; font:12px inherit; }.room-question input:focus { border-color:#c98c5f; }.room-question button { width:36px; border:0; border-radius:5px; background:#c98c5f; color:#fff; cursor:pointer; }.room-question button:disabled { opacity:.5; cursor:default; }@media (max-width:720px) { .action-panel { right:10px; bottom:18px; width:calc(100% - 20px); padding:12px; } }
</style>
