<template>
  <div class="skeleton-card">
    <div class="sk-meta"></div>
    <div class="sk-title"></div>
    <div class="sk-title sk-title--short"></div>
    <div class="sk-desc"></div>
    <div class="sk-desc sk-desc--short"></div>
    <div class="sk-tags">
      <div class="sk-tag"></div>
      <div class="sk-tag sk-tag--w2"></div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}
.skeleton-card {
  padding: 1.5rem;
  border-radius: 16px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-card);
  display: flex;
  flex-direction: column;
  gap: .7rem;
}
.sk-meta, .sk-title, .sk-desc, .sk-tag {
  border-radius: 6px;
  background: linear-gradient(90deg,
    var(--qi-bg-muted) 25%,
    var(--qi-bg-card)  50%,
    var(--qi-bg-muted) 75%);
  background-size: 800px 100%;
  animation: shimmer 1.4s infinite;
}
.sk-meta   { height: 12px; width: 120px; }
.sk-title  { height: 20px; width: 85%; }
.sk-title--short { width: 60%; }
.sk-desc   { height: 13px; width: 100%; }
.sk-desc--short { width: 70%; }
.sk-tags   { display: flex; gap: .5rem; margin-top: .25rem; }
.sk-tag    { height: 20px; width: 56px; border-radius: 999px; }
.sk-tag--w2 { width: 72px; }
</style>
