<script setup lang="ts">
import { useIntersection } from '@/composables/useIntersection'

withDefaults(defineProps<{
  delay?: number
}>(), {
  delay: 0,
})

const { el, isVisible } = useIntersection()
</script>

<template>
  <div
    ref="el"
    class="reveal-wrap"
    :class="{ 'is-visible': isVisible }"
    :style="{ transitionDelay: `${delay}ms` }"
  >
    <slot />
  </div>
</template>
