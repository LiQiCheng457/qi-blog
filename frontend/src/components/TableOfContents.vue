<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{ content: string }>()

interface Heading { id: string; text: string; level: number }

const headings  = ref<Heading[]>([])
const activeId  = ref('')

function slugify(text: string) {
  return text.trim().toLowerCase()
    .replace(/[^\w一-鿿\s-]/g, '')
    .replace(/\s+/g, '-')
}

function parseHeadings() {
  // 从 DOM 里读，保证和实际渲染一致
  const article = document.querySelector('.post-content')
  if (!article) return
  const els = article.querySelectorAll('h1,h2,h3')
  headings.value = []
  els.forEach(el => {
    const text  = el.textContent ?? ''
    const id    = slugify(text)
    el.id = id
    headings.value.push({ id, text, level: parseInt(el.tagName[1]) })
  })
}

function onScroll() {
  const ids = headings.value.map(h => h.id)
  for (let i = ids.length - 1; i >= 0; i--) {
    const el = document.getElementById(ids[i])
    if (el && el.getBoundingClientRect().top <= 120) {
      activeId.value = ids[i]
      return
    }
  }
  activeId.value = ids[0] ?? ''
}

function scrollTo(id: string) {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(() => {
  setTimeout(parseHeadings, 50)
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))
watch(() => props.content, () => setTimeout(parseHeadings, 50))
</script>

<template>
  <nav v-if="headings.length" class="toc">
    <p class="toc-title">目录</p>
    <ul class="toc-list">
      <li
        v-for="h in headings"
        :key="h.id"
        class="toc-item"
        :class="[`level-${h.level}`, { active: activeId === h.id }]"
        @click="scrollTo(h.id)"
      >
        {{ h.text }}
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.toc {
  position: sticky;
  top: 100px;
  padding: 1rem;
  background: var(--qi-bg-card);
  border: 1.5px solid var(--qi-border);
  border-radius: 14px;
  max-height: calc(100vh - 140px);
  overflow-y: auto;
  scrollbar-width: thin;
}
.toc-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--qi-ink-light);
  margin-bottom: .75rem;
}
.toc-list { list-style: none; display: flex; flex-direction: column; gap: 2px; }
.toc-item {
  font-size: 12.5px;
  color: var(--qi-ink-muted);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  line-height: 1.4;
  transition: all .15s;
  border-left: 2px solid transparent;
}
.toc-item:hover { color: var(--qi-primary); background: rgba(255,140,90,.06); }
.toc-item.active {
  color: var(--qi-primary);
  border-left-color: var(--qi-primary);
  background: rgba(255,140,90,.08);
  font-weight: 500;
}
.level-1 { padding-left: 8px; }
.level-2 { padding-left: 16px; font-size: 12px; }
.level-3 { padding-left: 24px; font-size: 11.5px; color: var(--qi-ink-light); }
</style>
