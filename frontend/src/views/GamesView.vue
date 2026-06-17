<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

interface GameCard {
  key: string
  tag: string
  name: string
  sub: string
  icon: string
  path: string
  desc: string
}

const games: GameCard[] = [
  {
    key: '2048',
    tag: '益智',
    name: '2048 · 起风了版',
    sub: '合并格子，一路玩到「起风了」',
    icon: '🌟',
    path: '/games/2048',
    desc: '经典 2048 玩法，格子变成了博客标签。从随笔合并到「起风了」，键盘方向键或 WASD 操作，手机可滑动。',
  },
]
</script>

<template>
  <div class="games-page">
    <section class="page-header">
      <span class="header-badge">游戏区 · Arcade</span>
      <h1 class="page-title">自己做的小游戏</h1>
      <p class="page-desc">
        一些很基础的小游戏，<span class="hl">用来玩玩</span>。
      </p>
    </section>

    <div class="games-grid">
      <article v-for="game in games" :key="game.key" class="game-card">
        <div class="card-top">
          <div class="game-icon">{{ game.icon }}</div>
          <div class="game-meta">
            <span class="game-tag">{{ game.tag }}</span>
            <h2 class="game-name">{{ game.name }}</h2>
            <p class="game-sub">{{ game.sub }}</p>
          </div>
        </div>
        <p class="game-desc">{{ game.desc }}</p>
        <button class="play-btn" @click="router.push(game.path)">开始游戏 →</button>
      </article>
    </div>
  </div>
</template>

<style scoped>
.games-page {
  min-height: 100vh;
  padding: 100px 1.5rem 4rem;
  max-width: 896px;
  margin: 0 auto;
  background: radial-gradient(circle at 50% 0%, rgba(255,209,102,.10), transparent 55%) var(--qi-bg);
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}
.header-badge {
  display: inline-block;
  font-size: .72rem; letter-spacing: .1em;
  color: var(--qi-primary);
  background: rgba(255,140,90,.1);
  padding: .25rem .75rem; border-radius: 999px;
  margin-bottom: .875rem;
}
.page-title {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 500; color: var(--qi-ink);
  margin: 0 0 .625rem; line-height: 1.25;
}
.page-desc { font-size: .95rem; color: var(--qi-ink-muted); margin: 0; }
.hl { color: var(--qi-primary); font-style: italic; }

.games-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.game-card {
  background: var(--qi-bg-card);
  border: 1px solid var(--qi-border);
  border-radius: 16px;
  padding: 1.25rem;
  display: flex; flex-direction: column; gap: .875rem;
  transition: box-shadow .25s, transform .25s;
}
.game-card:hover {
  box-shadow: 0 6px 24px rgba(0,0,0,.08);
  transform: translateY(-2px);
}

.card-top {
  display: flex; align-items: flex-start; gap: .875rem;
}
.game-icon {
  width: 44px; height: 44px; flex-shrink: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255,209,102,.25), rgba(255,140,90,.18));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.25rem;
}
.game-meta { min-width: 0; }
.game-tag {
  display: inline-block; font-size: .65rem; letter-spacing: .08em;
  color: var(--qi-primary); background: rgba(255,140,90,.1);
  padding: 1px 7px; border-radius: 999px; margin-bottom: .25rem;
}
.game-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.05rem; font-weight: 500; color: var(--qi-ink);
  margin: 0 0 .2rem;
}
.game-sub {
  font-size: .78rem; color: var(--qi-ink-light); margin: 0;
}

.game-desc {
  font-size: .82rem; color: var(--qi-ink-muted);
  line-height: 1.65; margin: 0;
}

.play-btn {
  align-self: flex-start;
  padding: .45rem 1.1rem;
  border-radius: 8px; border: none;
  background: var(--qi-primary); color: #fff;
  font-size: .84rem; font-weight: 500;
  cursor: pointer; transition: opacity .2s;
  margin-top: auto;
}
.play-btn:hover { opacity: .85; }

@media (max-width: 640px) {
  .games-grid { grid-template-columns: 1fr; }
}
</style>
