<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import QiMascot from '@/components/QiMascot.vue'
import ScrollReveal from '@/components/ScrollReveal.vue'
import { photosApi } from '@/api/photos'
import type { Photo } from '@/types'

const photos = ref<Photo[]>([])
const loading = ref(true)

onMounted(async () => {
  try { photos.value = await photosApi.list() }
  catch { /* 后端未启动时静默 */ }
  finally { loading.value = false }
})

const ALL = '全部'
const activeTag = ref(ALL)

const tags = computed(() => {
  const set = new Set(photos.value.map(p => p.tag))
  return [ALL, ...set]
})

const filtered = computed(() =>
  activeTag.value === ALL ? photos.value : photos.value.filter(p => p.tag === activeTag.value)
)

// 灯箱
const lightboxSrc = ref('')
const lightboxAlt = ref('')

function openLightbox(photo: Photo) {
  lightboxSrc.value = photo.url
  lightboxAlt.value = photo.alt
}

function closeLightbox() {
  lightboxSrc.value = ''
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') closeLightbox()
}

watch(lightboxSrc, val => {
  if (val) document.addEventListener('keydown', onKey)
  else document.removeEventListener('keydown', onKey)
})
</script>

<template>
  <div class="photos-page">
    <div class="photos-inner">

      <!-- 页头 -->
      <div class="photos-header">
        <div class="header-text">
          <ScrollReveal>
            <h1 class="page-title">相册</h1>
            <p class="page-subtitle">记录走过的地方，看见的光线，和某个还没忘掉的瞬间。</p>
          </ScrollReveal>
          <ScrollReveal :delay="150">
            <div class="filter-tabs" v-if="tags.length > 1">
              <button
                v-for="tag in tags"
                :key="tag"
                class="filter-tab"
                :class="{ active: activeTag === tag }"
                @click="activeTag = tag"
              >{{ tag }}</button>
            </div>
          </ScrollReveal>
        </div>
        <div class="header-mascot">
          <QiMascot state="think" size="medium" />
        </div>
      </div>

      <!-- 瀑布流网格 -->
      <ScrollReveal v-if="!loading && filtered.length > 0">
        <div class="masonry-grid">
          <div
            v-for="photo in filtered"
            :key="photo.id"
            class="masonry-item"
            @click="openLightbox(photo)"
          >
            <img :src="photo.url" :alt="photo.alt" loading="lazy" />
            <div class="masonry-overlay">
              <span class="overlay-tag">{{ photo.tag }}</span>
              <span class="overlay-alt">{{ photo.alt }}</span>
            </div>
          </div>
        </div>
      </ScrollReveal>

      <!-- 加载中 -->
      <div v-if="loading" class="empty-state">
        <QiMascot state="think" size="medium" />
        <p>正在加载照片…</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filtered.length === 0" class="empty-state">
        <QiMascot state="wave" size="medium" />
        <p>还没有照片，去后台上传第一张吧。</p>
      </div>

    </div>

    <!-- 灯箱 -->
    <Teleport to="body">
      <Transition name="lightbox">
        <div v-if="lightboxSrc" class="lightbox-overlay" @click.self="closeLightbox">
          <button class="lightbox-close" @click="closeLightbox">✕</button>
          <img :src="lightboxSrc" :alt="lightboxAlt" class="lightbox-img" />
          <p v-if="lightboxAlt" class="lightbox-caption">{{ lightboxAlt }}</p>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.photos-page {
  min-height: 100vh;
  padding-top: 80px;
  background: var(--qi-bg);
}

.photos-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 4rem 1.5rem 6rem;
}

/* 页头 */
.photos-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 3rem;
  gap: 2rem;
}

.header-text { flex: 1; }

.page-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 40px;
  font-weight: 500;
  color: var(--qi-ink);
  margin-bottom: .75rem;
}

.page-subtitle {
  font-size: 15px;
  color: var(--qi-ink-muted);
  margin-bottom: 2rem;
  line-height: 1.7;
}

.filter-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
}

.filter-tab {
  font-size: 13px;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: 999px;
  border: 1.5px solid var(--qi-border);
  background: transparent;
  color: var(--qi-ink-muted);
  cursor: pointer;
  transition: all .2s;
}

.filter-tab:hover,
.filter-tab.active {
  background: var(--qi-primary);
  border-color: var(--qi-primary);
  color: white;
}

.header-mascot {
  flex-shrink: 0;
  padding-top: .5rem;
}

/* 瀑布流 */
.masonry-grid {
  columns: 3;
  column-gap: .75rem;
}

.masonry-item {
  break-inside: avoid;
  margin-bottom: .75rem;
  border-radius: 10px;
  overflow: hidden;
  cursor: zoom-in;
  position: relative;
  background: var(--qi-bg-muted);
}

.masonry-item img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform .4s ease;
}

.masonry-item:hover img {
  transform: scale(1.04);
}

.masonry-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, .68) 0%,
    rgba(0, 0, 0, .08) 52%,
    rgba(0, 0, 0, .22) 100%
  );
  opacity: 0;
  transition: opacity .28s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: .75rem 1rem;
}

.masonry-item:hover .masonry-overlay {
  opacity: 1;
}

.overlay-tag {
  align-self: flex-start;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .03em;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .18);
  color: rgba(255, 255, 255, .92);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, .2);
}

.overlay-alt {
  color: white;
  font-size: 13px;
  line-height: 1.6;
  text-shadow: 0 1px 6px rgba(0, 0, 0, .6);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 6rem 0;
  color: var(--qi-ink-muted);
  font-size: 14px;
  text-align: center;
}

.empty-state code {
  font-family: monospace;
  background: var(--qi-bg-muted);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--qi-primary);
}

/* 响应式 */
@media (max-width: 960px) {
  .masonry-grid { columns: 2; }
  .header-mascot { display: none; }
}

@media (max-width: 600px) {
  .photos-page { padding-top: 72px; }
  .photos-inner { padding: 2rem 1rem 4rem; }
  .page-title { font-size: 28px; }
  .masonry-grid { columns: 1; }
}
</style>

<!-- 灯箱样式不走 scoped（Teleport 渲染到 body 外） -->
<style>
.lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(0, 0, 0, .88);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  cursor: zoom-out;
}

.lightbox-img {
  max-width: 90vw;
  max-height: 82vh;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 24px 80px rgba(0,0,0,.5);
  cursor: default;
}

.lightbox-caption {
  margin-top: 1rem;
  color: rgba(255,255,255,.75);
  font-size: 13px;
  text-align: center;
}

.lightbox-close {
  position: absolute;
  top: 1.25rem;
  right: 1.5rem;
  background: rgba(255,255,255,.12);
  border: none;
  color: white;
  font-size: 18px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background .2s;
}

.lightbox-close:hover { background: rgba(255,255,255,.22); }

.lightbox-enter-active, .lightbox-leave-active { transition: opacity .22s ease; }
.lightbox-enter-from, .lightbox-leave-to { opacity: 0; }
</style>
