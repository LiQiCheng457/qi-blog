<script setup lang="ts">
import { useTyping } from '@/composables/useTyping'

const props = withDefaults(defineProps<{
  text: string
  delay?: number
  speed?: number
  tag?: string
}>(), {
  delay: 0,
  speed: 60,
  tag: 'span',
})

const { displayed, done } = useTyping(props.text, { delay: props.delay, speed: props.speed })
</script>

<template>
  <component :is="tag">
    {{ displayed }}<span v-if="!done" class="cursor">|</span>
  </component>
</template>

<style scoped>
.cursor {
  display: inline-block;
  color: var(--qi-primary);
  font-weight: 300;
  animation: blink 0.8s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0; }
}
</style>
