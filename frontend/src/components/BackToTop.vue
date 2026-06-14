<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const visible = ref(false)

function onScroll() { visible.value = window.scrollY > 320 }
function scrollTop() { window.scrollTo({ top: 0, behavior: 'smooth' }) }

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <Transition name="btt">
    <button v-if="visible" class="btt" @click="scrollTop" title="回到顶部" aria-label="回到顶部">
      ↑
    </button>
  </Transition>
</template>

<style scoped>
.btt {
  position: fixed;
  left: 2rem;
  bottom: 2.5rem;
  width: 38px; height: 38px;
  border-radius: 50%;
  background: var(--qi-bg-card);
  color: var(--qi-ink-muted);
  font-size: 15px;
  font-weight: 600;
  border: 1.5px solid var(--qi-border);
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0, 0, 0, .08);
  backdrop-filter: blur(10px);
  transition: transform .2s, border-color .2s, color .2s, box-shadow .2s;
  z-index: 80;
  display: flex; align-items: center; justify-content: center;
}
.btt:hover {
  transform: translateY(-3px);
  border-color: var(--qi-primary);
  color: var(--qi-primary);
  box-shadow: 0 4px 16px rgba(255, 140, 90, .2);
}

.btt-enter-active, .btt-leave-active { transition: opacity .25s, transform .25s; }
.btt-enter-from, .btt-leave-to { opacity: 0; transform: translateY(12px); }
</style>
