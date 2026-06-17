<script setup lang="ts">
import CalendarWidget from '@/components/CalendarWidget.vue'
import PomodoroWidget from '@/components/PomodoroWidget.vue'
import FortuneWidget from '@/components/FortuneWidget.vue'
import WishingWellWidget from '@/components/WishingWellWidget.vue'

type ToolKey = 'calendar' | 'fortune' | 'pomodoro' | 'wish'

interface ToolMeta {
  key: ToolKey
  tag: string
  name: string
  sub: string
  icon: string
}

// 顺序经过排布，使瀑布流两列高度更接近
// 左列：日历(高) + 迷信指数(高)  右列：番茄钟(矮) + 许愿池(矮)
const tools: ToolMeta[] = [
  { key: 'calendar', tag: '时间', name: '实时日历',     sub: '看时间，也记日程',      icon: '🕰️' },
  { key: 'fortune',  tag: '玄学', name: '今日迷信指数', sub: '每日一签，认真胡说',    icon: '☯︎' },
  { key: 'pomodoro', tag: '专注', name: '番茄钟',       sub: '专注 25 分，休息 5 分', icon: '🍅' },
  { key: 'wish',     tag: '许愿', name: '赛博许愿池',   sub: '扔个愿望，捞个共鸣',    icon: '🪙' },
]
</script>

<template>
  <div class="tools-page">
    <!-- Hero -->
    <section class="page-header">
      <span class="header-badge">工具箱 · Toolkit</span>
      <h1 class="page-title">随手写的小东西</h1>
      <p class="page-desc">
        不是为了效率，只是希望偶尔打开它们能让你<span class="hl">慢一秒</span>。
      </p>
    </section>

    <!-- 瀑布流栅格 -->
    <div class="tools-grid">
      <article v-for="meta in tools" :key="meta.key" class="tool-card">
        <header class="tool-card-header">
          <div class="tool-icon">{{ meta.icon }}</div>
          <div class="tool-meta">
            <span class="tool-tag">{{ meta.tag }}</span>
            <h2 class="tool-name">{{ meta.name }}</h2>
            <p class="tool-sub">{{ meta.sub }}</p>
          </div>
        </header>

        <div class="tool-body">
          <CalendarWidget     v-if="meta.key === 'calendar'" />
          <PomodoroWidget     v-else-if="meta.key === 'pomodoro'" />
          <FortuneWidget      v-else-if="meta.key === 'fortune'" />
          <WishingWellWidget  v-else-if="meta.key === 'wish'" />
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.tools-page {
  min-height: 100vh;
  padding: 96px 0 5rem;
  background:
    radial-gradient(circle at 50% 0%, rgba(255, 209, 102, 0.10), transparent 55%),
    radial-gradient(circle at 0% 30%, rgba(255, 140, 90, 0.05), transparent 50%),
    var(--qi-bg);
}

/* ── Hero ───────────────────────────────────────────────────── */
.page-header {
  text-align: center;
  padding: 2.75rem 1.5rem 2.5rem;
  max-width: 680px;
  margin: 0 auto;
}
.header-badge {
  display: inline-block;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .12em;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(255, 140, 90, 0.1);
  color: var(--qi-primary);
  margin-bottom: 1.1rem;
}
.page-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--qi-ink);
  margin: 0 0 .85rem;
  letter-spacing: .02em;
  line-height: 1.25;
}
.page-desc {
  font-size: .95rem;
  color: var(--qi-ink-muted);
  line-height: 1.75;
  margin: 0;
}
.page-desc .hl {
  color: var(--qi-primary);
  font-weight: 600;
  margin: 0 .15em;
}

/* ── 瀑布流栅格（CSS columns 实现） ─────────────────────────── */
.tools-grid {
  max-width: 1024px;
  margin: 0 auto;
  padding: 0 1.5rem;
  column-count: 2;
  column-gap: 1.75rem;
}

/* ── 单张卡片 ───────────────────────────────────────────────── */
.tool-card {
  display: block;
  width: 100%;
  break-inside: avoid;
  -webkit-column-break-inside: avoid;
  page-break-inside: avoid;
  margin-bottom: 1.75rem;
  background: var(--qi-bg-card);
  border: 1px solid var(--qi-border);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(58, 42, 26, 0.04);
  transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}
.tool-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 36px rgba(58, 42, 26, 0.09);
  border-color: rgba(255, 140, 90, 0.28);
}

/* 头部 */
.tool-card-header {
  display: flex;
  align-items: flex-start;
  gap: .85rem;
  padding: 1.1rem 1.25rem 1rem;
  border-bottom: 1px solid var(--qi-border);
}
.tool-icon {
  width: 38px; height: 38px;
  border-radius: 11px;
  background: linear-gradient(135deg, rgba(255, 140, 90, .12), rgba(255, 209, 102, .12));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.15rem;
  flex-shrink: 0;
}
.tool-meta {
  display: flex;
  flex-direction: column;
  gap: .2rem;
  min-width: 0;
  flex: 1;
}
.tool-tag {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  font-size: .65rem;
  font-weight: 700;
  letter-spacing: .12em;
  padding: 1px 7px;
  border-radius: 999px;
  background: rgba(255, 140, 90, 0.1);
  color: var(--qi-primary);
}
.tool-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--qi-ink);
  margin: .15rem 0 0;
  line-height: 1.3;
}
.tool-sub {
  font-size: .72rem;
  color: var(--qi-ink-light);
  margin: 0;
  line-height: 1.5;
}

.tool-body { min-height: 0; }

/* ── 响应式 ───────────────────────────────────────────────── */
@media (max-width: 860px) {
  .tools-grid { column-count: 1; max-width: 480px; }
}
@media (max-width: 480px) {
  .page-title { font-size: 1.85rem; }
  .tools-grid { padding: 0 1rem; }
  .tool-card  { margin-bottom: 1.25rem; }
  .tools-page { padding-top: 80px; }
}
</style>
