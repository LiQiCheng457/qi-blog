<script setup lang="ts">
import QiMascot from '@/components/QiMascot.vue'
</script>

<template>
  <div class="notfound-page">
    <div class="notfound-inner">
      <QiMascot state="wake" size="medium" />
      <h1 class="notfound-code">404</h1>
      <h2 class="notfound-title">这里没有风</h2>
      <p class="notfound-desc">你要找的页面迷路了，风把它吹走了</p>
      <RouterLink to="/" class="notfound-btn">回到首页 →</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.notfound-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--qi-bg);
}

.notfound-inner {
  text-align: center;
  animation: fadeUp 0.6s ease both;
}

.notfound-code {
  font-family: 'Noto Serif SC', serif;
  font-size: 96px;
  font-weight: 700;
  color: var(--qi-primary);
  opacity: 0.3;
  line-height: 1;
  margin: 1rem 0 0.5rem;
}

.notfound-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 28px;
  font-weight: 500;
  color: var(--qi-ink);
  margin-bottom: 0.75rem;
}

.notfound-desc {
  font-size: 15px;
  color: var(--qi-ink-muted);
  margin-bottom: 2rem;
}

.notfound-btn {
  display: inline-block;
  padding: 10px 28px;
  border-radius: 999px;
  background: var(--qi-primary);
  color: white;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  transition: opacity 0.2s, transform 0.2s;
}

.notfound-btn:hover {
  opacity: 0.88;
  transform: translateY(-2px);
}
</style>
