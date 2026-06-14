<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <div class="section-title">
    <h2 class="title">{{ title }}</h2>
    <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
  </div>
</template>

<style scoped>
.section-title {
  margin-bottom: 2.5rem;
}

.title {
  font-family: 'Noto Serif SC', serif;
  font-size: 32px;
  font-weight: 500;
  color: var(--qi-ink);
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 15px;
  color: var(--qi-ink-muted);
}
</style>
