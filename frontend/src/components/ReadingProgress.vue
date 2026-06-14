<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const progress = ref(0)

function onScroll() {
  const el  = document.documentElement
  const top = el.scrollTop || document.body.scrollTop
  const h   = el.scrollHeight - el.clientHeight
  progress.value = h > 0 ? Math.min(100, (top / h) * 100) : 0
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <div class="reading-progress">
    <div class="bar" :style="{ width: progress + '%' }"></div>
  </div>
</template>

<style scoped>
.reading-progress {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: var(--qi-progress-h, 3px);
  z-index: 200;
  background: transparent;
}
.bar {
  height: 100%;
  background: linear-gradient(90deg, var(--qi-primary), var(--qi-accent));
  transition: width .1s linear;
  border-radius: 0 2px 2px 0;
  box-shadow: 0 0 6px rgba(255,140,90,.5);
}
</style>
