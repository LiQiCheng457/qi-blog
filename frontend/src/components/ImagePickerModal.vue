<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { photosApi } from '@/api/photos'
import type { Photo } from '@/types'

defineProps<{ current?: string }>()
const emit = defineEmits<{
  (e: 'select', url: string): void
  (e: 'close'): void
}>()

const photos  = ref<Photo[]>([])
const loading = ref(true)
const search  = ref('')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return photos.value
  return photos.value.filter(p => p.alt.toLowerCase().includes(q) || p.tag.toLowerCase().includes(q))
})

onMounted(async () => {
  try { photos.value = await photosApi.list() }
  finally { loading.value = false }
})
</script>

<template>
  <div class="picker-overlay" @click.self="emit('close')">
    <div class="picker-modal">
      <div class="picker-header">
        <h3>从相册选择封面</h3>
        <button class="close-btn" @click="emit('close')">×</button>
      </div>

      <div class="picker-search">
        <input v-model="search" type="text" placeholder="搜索描述或标签…" class="search-input" />
      </div>

      <div v-if="loading" class="picker-empty">加载中…</div>
      <div v-else-if="filtered.length === 0" class="picker-empty">没有匹配的图片</div>
      <div v-else class="picker-grid">
        <button
          v-for="photo in filtered"
          :key="photo.id"
          class="picker-item"
          :class="{ selected: photo.url === current }"
          @click="emit('select', photo.url); emit('close')"
        >
          <img :src="photo.url" :alt="photo.alt" class="picker-thumb" />
          <span v-if="photo.alt" class="picker-label">{{ photo.alt }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.picker-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.5);
  display: flex; align-items: center; justify-content: center; z-index: 1100;
}
.picker-modal {
  width: 720px; max-width: 95vw; max-height: 85vh;
  background: var(--qi-bg-card); border-radius: 18px;
  box-shadow: 0 20px 60px rgba(0,0,0,.25);
  display: flex; flex-direction: column; overflow: hidden;
}
.picker-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.1rem 1.5rem; border-bottom: 1px solid var(--qi-border); flex-shrink: 0;
}
.picker-header h3 { font-family:'Noto Serif SC',serif; font-size:16px; font-weight:500; color:var(--qi-ink); }
.close-btn { font-size:22px; background:none; border:none; color:var(--qi-ink-light); cursor:pointer; line-height:1; }
.picker-search { padding: .75rem 1.5rem; border-bottom: 1px solid var(--qi-border); flex-shrink: 0; }
.search-input {
  width: 100%; padding: 7px 12px; border-radius: 8px;
  border: 1.5px solid var(--qi-border); background: var(--qi-bg);
  font-size: 13.5px; color: var(--qi-ink); outline: none; font-family: inherit;
}
.search-input:focus { border-color: var(--qi-primary); }
.picker-empty { padding: 3rem; text-align: center; color: var(--qi-ink-light); font-size: 14px; }
.picker-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: .75rem; padding: 1rem 1.5rem; overflow-y: auto;
}
.picker-item {
  all: unset; cursor: pointer; border-radius: 10px; overflow: hidden;
  border: 2px solid transparent; transition: border-color .15s, transform .15s;
  display: flex; flex-direction: column;
}
.picker-item:hover { border-color: var(--qi-primary); transform: translateY(-2px); }
.picker-item.selected { border-color: var(--qi-primary); box-shadow: 0 0 0 3px rgba(255,140,90,.25); }
.picker-thumb { width: 100%; height: 100px; object-fit: cover; display: block; }
.picker-label {
  font-size: 11px; color: var(--qi-ink-muted); padding: 4px 6px;
  background: var(--qi-bg); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;
}
</style>
