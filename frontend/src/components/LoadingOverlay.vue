<script setup lang="ts">
defineProps<{ show: boolean }>()
</script>

<template>
  <Transition name="qi-loading">
    <div v-if="show" class="loading-wrap">
      <div class="loading-inner">
        <img src="/animations/qi_wind_medium.webp" alt="" class="loading-mascot" />
        <p class="loading-text">起风了</p>
        <div class="loading-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.loading-wrap {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: var(--qi-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: .75rem;
}

.loading-mascot {
  width: 120px;
  height: 120px;
  object-fit: contain;
  animation: mascot-float 2.4s ease-in-out infinite;
}

.loading-text {
  font-size: 15px;
  font-weight: 500;
  color: var(--qi-ink-muted);
  letter-spacing: .2em;
  margin: 0;
}

.loading-dots {
  display: flex;
  gap: 6px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--qi-primary);
  animation: dot-pulse 1.2s ease-in-out infinite;
}
.loading-dots span:nth-child(2) { animation-delay: .2s; }
.loading-dots span:nth-child(3) { animation-delay: .4s; }

@keyframes mascot-float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-8px); }
}

@keyframes dot-pulse {
  0%, 100% { opacity: .25; transform: scale(.8); }
  50%      { opacity: 1;   transform: scale(1.15); }
}

/* 进出场动画 */
.qi-loading-enter-active { transition: opacity .25s ease; }
.qi-loading-leave-active { transition: opacity .35s ease; }
.qi-loading-enter-from,
.qi-loading-leave-to    { opacity: 0; }
</style>
