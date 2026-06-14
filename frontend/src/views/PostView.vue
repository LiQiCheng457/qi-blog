<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { postsApi } from '@/api/posts'
import ReadingProgress from '@/components/ReadingProgress.vue'
import TableOfContents from '@/components/TableOfContents.vue'
import CommentSection from '@/components/CommentSection.vue'
import type { Post } from '@/types'

const route   = useRoute()
const router  = useRouter()
const post    = ref<Post | null>(null)
const prevPost = ref<{ slug: string; title: string } | null>(null)
const nextPost = ref<{ slug: string; title: string } | null>(null)
const loading  = ref(true)
const lightboxSrc = ref('')
const lightboxAlt = ref('')

marked.setOptions({
  // @ts-ignore
  highlight(code: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, { language: lang }).value
    return hljs.highlightAuto(code).value
  }
})

async function load(slug: string) {
  loading.value = true
  try {
    const [p, adj] = await Promise.all([
      postsApi.get(slug),
      postsApi.adjacent(slug).catch(() => ({ prev: null, next: null })),
    ])
    post.value     = p
    prevPost.value = adj.prev
    nextPost.value = adj.next
    await nextTick()
    injectCopyButtons()
    injectImageZoom()
  } catch {
    router.replace('/404')
  } finally {
    loading.value = false
  }
}

onMounted(() => load(route.params.slug as string))
watch(() => route.params.slug, slug => slug && load(slug as string))

const renderedContent = computed(() => post.value ? marked(post.value.content) as string : '')

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// ── 图片点击放大 ───────────────────────────────────────────────
function injectImageZoom() {
  const article = document.querySelector('.post-content')
  if (!article) return
  article.querySelectorAll('img').forEach(img => {
    if (img.dataset.zoomed) return
    img.dataset.zoomed = '1'
    img.style.cursor = 'zoom-in'
    img.addEventListener('click', () => {
      lightboxSrc.value = img.src
      lightboxAlt.value = img.alt
    })
  })
}

function closeLightbox() {
  lightboxSrc.value = ''
}

function onLightboxKey(e: KeyboardEvent) {
  if (e.key === 'Escape') closeLightbox()
}

watch(lightboxSrc, val => {
  if (val) document.addEventListener('keydown', onLightboxKey)
  else document.removeEventListener('keydown', onLightboxKey)
})

// ── 代码块复制按钮 ─────────────────────────────────────────────
function injectCopyButtons() {
  const article = document.querySelector('.post-content')
  if (!article) return
  article.querySelectorAll('pre').forEach(pre => {
    if (pre.querySelector('.copy-btn')) return   // 已注入过
    const btn = document.createElement('button')
    btn.className = 'copy-btn'
    btn.textContent = '复制'
    btn.addEventListener('click', async () => {
      const code = pre.querySelector('code')?.innerText ?? ''
      await navigator.clipboard.writeText(code).catch(() => {})
      btn.textContent = '已复制!'
      btn.classList.add('copied')
      setTimeout(() => { btn.textContent = '复制'; btn.classList.remove('copied') }, 2000)
    })
    pre.style.position = 'relative'
    pre.appendChild(btn)
  })
}
</script>

<template>
  <!-- 阅读进度条 -->
  <ReadingProgress />

  <div class="post-page">
    <!-- 骨架屏 -->
    <div v-if="loading" class="post-inner">
      <div class="skeleton-header">
        <div class="sk sk-tag"></div>
        <div class="sk sk-title"></div>
        <div class="sk sk-meta"></div>
      </div>
      <div class="skeleton-body">
        <div v-for="i in 6" :key="i" class="sk sk-line" :style="{ width: [100,88,95,72,100,80][i-1]+'%' }"></div>
      </div>
    </div>

    <div v-else-if="post" class="post-inner">
      <header class="post-header">
        <div class="post-tags">
          <span v-for="tag in post.tags" :key="tag" class="post-tag">{{ tag }}</span>
        </div>
        <h1 class="post-title">{{ post.title }}</h1>
        <div class="post-meta">
          <time :datetime="post.createdAt">{{ formatDate(post.createdAt) }}</time>
          <span>·</span>
          <span>{{ post.readingTime }} 分钟阅读</span>
          <span>·</span>
          <span>{{ post.viewCount }} 次阅读</span>
        </div>
      </header>

      <div class="post-layout">
        <article class="post-content" v-html="renderedContent"></article>

        <!-- 侧边栏：目录 -->
        <aside class="post-aside">
          <TableOfContents :content="renderedContent" />
        </aside>
      </div>

      <!-- 上下篇导航 -->
      <nav class="post-adj-nav">
        <RouterLink v-if="prevPost" :to="`/blog/${prevPost.slug}`" class="adj-link adj-link--prev">
          <span class="adj-label">← 上一篇</span>
          <span class="adj-title">{{ prevPost.title }}</span>
        </RouterLink>
        <span v-else class="adj-empty"></span>
        <RouterLink v-if="nextPost" :to="`/blog/${nextPost.slug}`" class="adj-link adj-link--next">
          <span class="adj-label">下一篇 →</span>
          <span class="adj-title">{{ nextPost.title }}</span>
        </RouterLink>
        <span v-else class="adj-empty"></span>
      </nav>

      <div class="post-bottom-nav">
        <RouterLink to="/blog" class="back-link">← 返回文章列表</RouterLink>
      </div>

      <CommentSection :post-slug="post.slug" />
    </div>
  </div>

  <Teleport to="body">
    <Transition name="lightbox">
      <div v-if="lightboxSrc" class="lightbox-overlay" @click="closeLightbox">
        <img :src="lightboxSrc" :alt="lightboxAlt" class="lightbox-img" @click.stop />
        <button class="lightbox-close" aria-label="关闭" @click="closeLightbox">✕</button>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.post-page { min-height: 100vh; padding-top: 80px; background: var(--qi-bg); }
.post-inner { max-width: 960px; margin: 0 auto; padding: 4rem 1.5rem; }

/* 骨架屏 */
@keyframes shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position: 600px 0; }
}
.sk {
  border-radius: 6px;
  background: linear-gradient(90deg, var(--qi-bg-muted) 25%, var(--qi-bg-card) 50%, var(--qi-bg-muted) 75%);
  background-size: 1200px 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: .8rem;
}
.sk-tag  { height: 20px; width: 80px; border-radius: 999px; }
.sk-title { height: 36px; width: 70%; margin: .8rem 0; }
.sk-meta  { height: 14px; width: 200px; }
.sk-line  { height: 14px; }
.skeleton-header { margin-bottom: 2.5rem; padding-bottom: 2rem; border-bottom: 1px solid var(--qi-border); }
.skeleton-body { display: flex; flex-direction: column; gap: .6rem; }

/* 头部 */
.post-header { margin-bottom: 3rem; border-bottom: 1px solid var(--qi-border); padding-bottom: 2rem; }
.post-tags { display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: 1rem; }
.post-tag { font-size: 12px; font-weight: 500; padding: 3px 12px; border-radius: 999px; background: rgba(255,140,90,.12); color: var(--qi-primary); }
.post-title { font-family: 'Noto Serif SC', serif; font-size: clamp(26px, 4vw, 40px); font-weight: 500; color: var(--qi-ink); line-height: 1.35; margin-bottom: 1rem; }
.post-meta { display: flex; gap: .5rem; font-size: 13px; color: var(--qi-ink-light); flex-wrap: wrap; }

/* 布局 */
.post-layout { display: grid; grid-template-columns: 1fr 220px; gap: 3rem; align-items: start; }

/* 正文 */
.post-content { min-width: 0; line-height: 1.9; color: var(--qi-ink); }
.post-content :deep(h1),
.post-content :deep(h2),
.post-content :deep(h3) { font-family: 'Noto Serif SC', serif; font-weight: 500; margin: 2rem 0 1rem; color: var(--qi-ink); }
.post-content :deep(h1) { font-size: 28px; }
.post-content :deep(h2) { font-size: 22px; }
.post-content :deep(h3) { font-size: 18px; }
.post-content :deep(p) { margin-bottom: 1.2rem; color: var(--qi-ink-muted); }
.post-content :deep(pre) {
  background: var(--qi-bg-card);
  border-radius: 12px;
  padding: 1.25rem 1.25rem 1.25rem;
  overflow-x: auto;
  margin: 1.5rem 0;
  border: 1px solid var(--qi-border);
  position: relative;
}
.post-content :deep(code) { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 14px; }
.post-content :deep(:not(pre) > code) { background: rgba(255,140,90,.1); color: var(--qi-primary); padding: 2px 6px; border-radius: 4px; font-size: 13px; }
.post-content :deep(blockquote) { border-left: 3px solid var(--qi-primary); margin: 1.5rem 0; padding: .5rem 0 .5rem 1.25rem; color: var(--qi-ink-muted); font-style: italic; }
.post-content :deep(ul), .post-content :deep(ol) { padding-left: 1.5rem; margin-bottom: 1.2rem; }
.post-content :deep(li) { margin-bottom: .3rem; color: var(--qi-ink-muted); }
.post-content :deep(a) { color: var(--qi-primary); text-decoration: underline; text-underline-offset: 3px; }
.post-content :deep(img) { max-width: 100%; border-radius: 10px; margin: 1rem 0; }
.post-content :deep(table) { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 14px; }
.post-content :deep(th), .post-content :deep(td) { border: 1px solid var(--qi-border); padding: .6rem 1rem; }
.post-content :deep(th) { background: var(--qi-bg-muted); font-weight: 600; }

/* 复制按钮（全局注入） */
:global(.copy-btn) {
  position: absolute;
  top: .6rem; right: .6rem;
  padding: 3px 10px;
  font-size: 11px; font-weight: 500;
  background: var(--qi-bg-muted);
  color: var(--qi-ink-muted);
  border: 1px solid var(--qi-border);
  border-radius: 6px;
  cursor: pointer;
  opacity: 0;
  transition: opacity .2s, background .2s;
}
:global(pre:hover .copy-btn) { opacity: 1; }
:global(.copy-btn.copied) { background: rgba(168,216,192,.3); color: #3a8c6a; border-color: #a8d8c0; }

/* 上下篇 */
.post-adj-nav {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--qi-border);
}
.adj-link {
  display: flex;
  flex-direction: column;
  gap: .3rem;
  padding: 1rem;
  border-radius: 12px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-card);
  text-decoration: none;
  transition: border-color .2s, background .2s;
}
.adj-link:hover { border-color: var(--qi-primary); background: rgba(255,140,90,.04); }
.adj-link--next { text-align: right; }
.adj-label { font-size: 11px; font-weight: 600; color: var(--qi-ink-light); text-transform: uppercase; letter-spacing: .05em; }
.adj-title { font-size: 14px; font-weight: 500; color: var(--qi-ink); line-height: 1.4; }
.adj-empty { display: block; }

/* 底部返回 */
.post-bottom-nav { margin-top: 1.5rem; }
.back-link { font-size: 14px; color: var(--qi-ink-muted); text-decoration: none; transition: color .2s; }
.back-link:hover { color: var(--qi-primary); }

@media (max-width: 768px) {
  .post-layout { grid-template-columns: 1fr; }
  .post-aside  { display: none; }
  .post-adj-nav { grid-template-columns: 1fr; }
}

/* 图片 lightbox */
:global(.lightbox-overlay) {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-out;
}
:global(.lightbox-img) {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.6);
  cursor: default;
}
:global(.lightbox-close) {
  position: absolute;
  top: 1.25rem;
  right: 1.75rem;
  font-size: 22px;
  line-height: 1;
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
:global(.lightbox-close:hover) {
  background: rgba(255, 255, 255, 0.22);
  color: #fff;
}
:global(.lightbox-enter-active),
:global(.lightbox-leave-active) { transition: opacity 0.2s ease; }
:global(.lightbox-enter-from),
:global(.lightbox-leave-to) { opacity: 0; }
</style>
