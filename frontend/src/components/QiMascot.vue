<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useQiMascot } from '@/composables/useQiMascot'
import type { MascotState, MascotSize } from '@/types'

const props = withDefaults(defineProps<{
  state?: MascotState
  size?: MascotSize
  autoSwitch?: boolean
}>(), {
  state: 'wave',
  size: 'medium',
  autoSwitch: false,
})

const { currentState } = useQiMascot()

const activeState = computed(() => props.autoSwitch ? currentState.value : props.state)

const sizeMap: Record<MascotSize, string> = {
  small: '240px',
  medium: '320px',
  large: '400px',
}

const sizeStyle = computed(() => ({
  width: sizeMap[props.size],
  height: sizeMap[props.size],
}))

const imageStyle = computed(() => ({
  ...sizeStyle.value,
}))

// 切换时淡入淡出
const opacity = ref(1)
watch(activeState, () => {
  opacity.value = 0
  setTimeout(() => { opacity.value = 1 }, 150)
})

// singing 暂无专属资源，用 wave 代替
const stateAlias: Partial<Record<MascotState, MascotState>> = {
  singing: 'wave',
}

const base = import.meta.env.BASE_URL

function webpSrc(state: MascotState) {
  const s = stateAlias[state] ?? state
  return `${base}animations/qi_${s}_${props.size}.webp`
}

// GIF 仅 wake_medium 有对应尺寸，其余 fallback 到 small_transp
function gifSrc(state: MascotState) {
  const s = stateAlias[state] ?? state
  if (s === 'wake') return `${base}animations/qi_wake_medium.gif`
  return `${base}animations/qi_${s}_small_transp.gif`
}
</script>

<template>
  <div
    class="qi-mascot"
    :style="{ ...sizeStyle, opacity, transition: 'opacity 0.3s ease' }"
  >
    <picture>
      <source :srcset="webpSrc(activeState)" type="image/webp" />
      <img
        class="qi-mascot-img"
        :src="gifSrc(activeState)"
        :alt="`水豚祁 - ${activeState}`"
        :style="imageStyle"
      />
    </picture>
  </div>
</template>

<style scoped>
.qi-mascot {
  overflow: hidden;
  clip-path: inset(2.5% round 2px);
}

.qi-mascot-img {
  display: block;
  object-fit: contain;
  transform: scale(1.045);
  transform-origin: center;
  clip-path: inset(2.5%);
}

:global([data-theme="dark"] .qi-mascot) {
  clip-path: inset(3.5% round 2px);
}

:global([data-theme="dark"] .qi-mascot-img) {
  transform: scale(1.065);
  clip-path: inset(3.5%);
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.22));
}
</style>
