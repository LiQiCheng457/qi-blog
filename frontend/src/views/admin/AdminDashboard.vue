<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { use }          from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, BarChart, PieChart,
     GridComponent, TooltipComponent, LegendComponent, DataZoomComponent])

import { postsApi }    from '@/api/posts'
import { projectsApi } from '@/api/projects'
import { adminApi, type DashboardStats } from '@/api/admin'
import { useThemeStore } from '@/stores/theme'
import type { Post, Project } from '@/types'

const posts    = ref<Post[]>([])
const projects = ref<Project[]>([])
const stats    = ref<DashboardStats | null>(null)
const loading  = ref(true)
const theme    = useThemeStore()

onMounted(async () => {
  try {
    const [postsRes, projectsRes, statsRes] = await Promise.allSettled([
      postsApi.list(), projectsApi.list(), adminApi.stats(),
    ])
    if (postsRes.status    === 'fulfilled') posts.value    = postsRes.value
    if (projectsRes.status === 'fulfilled') projects.value = projectsRes.value
    if (statsRes.status    === 'fulfilled') stats.value    = statsRes.value
  } finally {
    loading.value = false
  }
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
function formatNum(n: number) {
  return n >= 10000 ? (n / 10000).toFixed(1) + 'w'
       : n >= 1000  ? (n / 1000).toFixed(1)  + 'k'
       : String(n)
}
function greet() {
  const h = new Date().getHours()
  if (h < 6)  return '夜深了，还在工作？'
  if (h < 11) return '早上好，今天想写点什么？'
  if (h < 14) return '午后时光，来看看博客数据'
  if (h < 18) return '下午好，继续创作吧'
  return '晚上好，今天过得怎么样？'
}

// ── ECharts 公共样式 ─────────────────────────────────────────────
const axisColor  = computed(() => theme.isDark ? '#6e5a4a' : '#b09a86')
const labelColor = computed(() => theme.isDark ? '#b09a86' : '#8a7060')

// ── 折线面积图：文章发布趋势 ──────────────────────────────────────
const postLineOpt = computed(() => {
  const months = (stats.value?.monthlyPosts ?? []).map(d => d.month)
  const counts = (stats.value?.monthlyPosts ?? []).map(d => d.count)
  return {
    backgroundColor: 'transparent',
    grid: { top: 28, right: 12, bottom: 28, left: 32, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(36,30,24,.9)',
      borderColor: 'rgba(255,140,90,.25)',
      textStyle: { color: '#f0e8dc', fontSize: 12 },
      formatter: (p: any) => `${p[0].name}<br/>发布 <b>${p[0].value}</b> 篇`,
    },
    xAxis: {
      type: 'category', data: months,
      axisLine: { lineStyle: { color: axisColor.value } },
      axisTick: { show: false },
      axisLabel: { color: labelColor.value, fontSize: 11 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value', minInterval: 1,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: labelColor.value, fontSize: 11 },
      splitLine: { lineStyle: { color: axisColor.value, opacity: .35, type: 'dashed' } },
    },
    series: [{
      type: 'line', data: counts, smooth: true,
      symbol: 'circle', symbolSize: 7,
      itemStyle: { color: '#ff8c5a', borderColor: '#fff', borderWidth: 2 },
      lineStyle: { color: '#ff8c5a', width: 2.5 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(255,140,90,.35)' },
            { offset: 1, color: 'rgba(255,140,90,.02)' },
          ],
        },
      },
      label: { show: true, position: 'top', color: '#ff8c5a', fontSize: 11, fontWeight: 600,
               formatter: (p: any) => p.value > 0 ? p.value : '' },
    }],
  }
})

// ── 折线面积图：评论活跃度 ────────────────────────────────────────
const commentLineOpt = computed(() => {
  const months = (stats.value?.monthlyComments ?? []).map(d => d.month)
  const counts = (stats.value?.monthlyComments ?? []).map(d => d.count)
  return {
    backgroundColor: 'transparent',
    grid: { top: 28, right: 12, bottom: 28, left: 32, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(36,30,24,.9)',
      borderColor: 'rgba(107,181,160,.25)',
      textStyle: { color: '#f0e8dc', fontSize: 12 },
      formatter: (p: any) => `${p[0].name}<br/>评论 <b>${p[0].value}</b> 条`,
    },
    xAxis: {
      type: 'category', data: months,
      axisLine: { lineStyle: { color: axisColor.value } },
      axisTick: { show: false },
      axisLabel: { color: labelColor.value, fontSize: 11 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value', minInterval: 1,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: labelColor.value, fontSize: 11 },
      splitLine: { lineStyle: { color: axisColor.value, opacity: .35, type: 'dashed' } },
    },
    series: [{
      type: 'line', data: counts, smooth: true,
      symbol: 'circle', symbolSize: 7,
      itemStyle: { color: '#6bb5a0', borderColor: '#fff', borderWidth: 2 },
      lineStyle: { color: '#6bb5a0', width: 2.5 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(107,181,160,.35)' },
            { offset: 1, color: 'rgba(107,181,160,.02)' },
          ],
        },
      },
      label: { show: true, position: 'top', color: '#6bb5a0', fontSize: 11, fontWeight: 600,
               formatter: (p: any) => p.value > 0 ? p.value : '' },
    }],
  }
})

// ── 饼图：发布 vs 草稿 ────────────────────────────────────────────
const pieOpt = computed(() => {
  const pub   = stats.value?.pubCount  ?? 0
  const total = stats.value?.postCount ?? 0
  const draft = total - pub
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(36,30,24,.9)',
      borderColor: 'rgba(255,140,90,.25)',
      textStyle: { color: '#f0e8dc', fontSize: 12 },
    },
    legend: {
      bottom: 4, left: 'center',
      textStyle: { color: labelColor.value, fontSize: 11 },
      itemWidth: 10, itemHeight: 10,
    },
    series: [{
      type: 'pie', radius: ['48%', '72%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: false,
      label: {
        show: true, position: 'center',
        formatter: () => `${total ? Math.round(pub / total * 100) : 0}%`,
        fontSize: 20, fontWeight: 800, color: '#ff8c5a',
      },
      itemStyle: { borderRadius: 6, borderColor: 'transparent', borderWidth: 2 },
      data: [
        { value: pub,   name: `已发布 ${pub}`,   itemStyle: { color: '#ff8c5a' } },
        { value: Math.max(draft, 0), name: `草稿 ${draft}`,
          itemStyle: { color: theme.isDark ? '#3a2e26' : '#e8ddd4' } },
      ],
    }],
  }
})

// ── 横向柱图：Top 5 阅读量 ────────────────────────────────────────
const TOP_COLORS = ['#ff8c5a', '#ffb347', '#6bb5a0', '#82b1ff', '#c97ef0']
const topBarOpt  = computed(() => {
  const tp = [...(stats.value?.topPosts ?? [])].reverse()
  return {
    backgroundColor: 'transparent',
    grid: { top: 8, right: 60, bottom: 8, left: 8, containLabel: true },
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'none' },
      backgroundColor: 'rgba(36,30,24,.9)',
      borderColor: 'rgba(255,140,90,.25)',
      textStyle: { color: '#f0e8dc', fontSize: 12 },
      formatter: (p: any) => `${p[0].name}<br/>阅读量 <b>${p[0].value}</b>`,
    },
    xAxis: { type: 'value', show: false },
    yAxis: {
      type: 'category',
      data: tp.map(p => p.title.length > 14 ? p.title.slice(0, 14) + '…' : p.title),
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: labelColor.value, fontSize: 12 },
    },
    series: [{
      type: 'bar', barMaxWidth: 16, barMinHeight: 4,
      data: tp.map((p, i) => ({
        value: p.views,
        itemStyle: { color: TOP_COLORS[tp.length - 1 - i], borderRadius: [0, 8, 8, 0] },
      })),
      label: {
        show: true, position: 'right',
        color: labelColor.value, fontSize: 11,
      },
    }],
  }
})
</script>

<template>
  <div class="dashboard">

    <!-- 欢迎栏 -->
    <div class="welcome-banner">
      <div class="welcome-left">
        <div class="welcome-greeting">{{ greet() }}</div>
        <div class="welcome-sub">起风了后台 · 数据概览</div>
      </div>
      <div class="welcome-actions">
        <RouterLink to="/admin/posts/new" class="action-primary">✏️ 写新文章</RouterLink>
        <RouterLink to="/admin/projects"  class="action-sec">🗂 管理项目</RouterLink>
      </div>
    </div>

    <!-- 骨架屏 -->
    <div v-if="loading" class="skeleton-row">
      <div v-for="i in 5" :key="i" class="skeleton-card"></div>
    </div>

    <template v-else>

      <!-- ── 统计卡片 ── -->
      <div class="stat-grid">
        <div class="stat-card" style="--c1:#ff8c5a;--c2:#ffb347">
          <div class="sc-icon">📝</div>
          <div class="sc-num">{{ stats?.postCount ?? posts.length }}</div>
          <div class="sc-label">篇文章</div>
          <div class="sc-sub">已发布 {{ stats?.pubCount ?? posts.length }}</div>
        </div>
        <div class="stat-card" style="--c1:#5b8ef0;--c2:#82b1ff">
          <div class="sc-icon">👁️</div>
          <div class="sc-num">{{ formatNum(stats?.viewTotal ?? 0) }}</div>
          <div class="sc-label">总阅读量</div>
          <div class="sc-sub">所有文章累计</div>
        </div>
        <div class="stat-card" style="--c1:#6bb5a0;--c2:#80cbc4">
          <div class="sc-icon">💬</div>
          <div class="sc-num">{{ stats?.commentCount ?? 0 }}</div>
          <div class="sc-label">条评论</div>
          <div class="sc-sub">读者留言</div>
        </div>
        <div class="stat-card" style="--c1:#c97ef0;--c2:#e1bee7">
          <div class="sc-icon">👤</div>
          <div class="sc-num">{{ stats?.userCount ?? 0 }}</div>
          <div class="sc-label">位读者</div>
          <div class="sc-sub">注册用户</div>
        </div>
        <div class="stat-card" style="--c1:#e07b54;--c2:#ffab76">
          <div class="sc-icon">🗂️</div>
          <div class="sc-num">{{ projects.length }}</div>
          <div class="sc-label">个项目</div>
          <div class="sc-sub">作品收录</div>
        </div>
      </div>

      <!-- ── 图表行：折线 + 饼图 ── -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-hd">
            <span class="chart-title">文章发布趋势</span>
            <span class="chart-badge">近 6 个月</span>
          </div>
          <VChart :option="postLineOpt" class="echart" autoresize />
        </div>

        <div class="chart-card">
          <div class="chart-hd">
            <span class="chart-title">评论活跃度</span>
            <span class="chart-badge" style="background:rgba(107,181,160,.12);color:#6bb5a0">近 6 个月</span>
          </div>
          <VChart :option="commentLineOpt" class="echart" autoresize />
        </div>

        <div class="chart-card chart-card--pie">
          <div class="chart-hd">
            <span class="chart-title">发布率</span>
          </div>
          <VChart :option="pieOpt" class="echart echart--pie" autoresize />
        </div>
      </div>

      <!-- ── Top 5 阅读量（横向柱图）── -->
      <div class="panel">
        <div class="panel-hd">
          <span class="panel-title">🔥 阅读量排行</span>
          <span class="panel-sub">Top 5 文章</span>
        </div>
        <VChart v-if="stats?.topPosts?.length" :option="topBarOpt"
          class="echart echart--bar" autoresize />
        <div v-else class="panel-empty">暂无阅读数据</div>
      </div>

      <!-- ── 最近文章 ── -->
      <div class="panel">
        <div class="panel-hd">
          <span class="panel-title">📋 最近文章</span>
          <RouterLink to="/admin/posts" class="panel-link">查看全部 →</RouterLink>
        </div>
        <div class="recent-list">
          <div v-for="post in posts.slice(0, 5)" :key="post.slug" class="recent-row">
            <div class="rr-left">
              <span class="rr-title">{{ post.title }}</span>
              <span class="rr-date">{{ formatDate(post.createdAt) }}</span>
            </div>
            <span class="rr-views">👁 {{ post.viewCount }}</span>
            <div class="rr-actions">
              <RouterLink :to="`/admin/posts/${post.slug}/edit`" class="rr-btn">编辑</RouterLink>
              <RouterLink :to="`/blog/${post.slug}`" target="_blank" class="rr-btn rr-btn--view">查看</RouterLink>
            </div>
          </div>
          <div v-if="posts.length === 0" class="panel-empty">还没有文章，去写第一篇吧！</div>
        </div>
      </div>

    </template>
  </div>
</template>

<style scoped>
.dashboard { width:100%; display:flex; flex-direction:column; gap:1.5rem; }

/* 欢迎栏 */
.welcome-banner { display:flex; align-items:center; justify-content:space-between; background:linear-gradient(135deg,rgba(255,140,90,.1) 0%,rgba(255,179,71,.06) 100%); border:1px solid rgba(255,140,90,.2); border-radius:18px; padding:1.5rem 2rem; }
.welcome-greeting { font-family:'Noto Serif SC',serif; font-size:22px; font-weight:500; color:var(--qi-ink); }
.welcome-sub { font-size:13px; color:var(--qi-ink-muted); margin-top:.2rem; }
.welcome-actions { display:flex; gap:.75rem; flex-shrink:0; }
.action-primary { display:inline-block; padding:9px 20px; border-radius:999px; background:var(--qi-primary); color:white; font-size:14px; font-weight:500; text-decoration:none; transition:opacity .2s; }
.action-primary:hover { opacity:.88; }
.action-sec { display:inline-block; padding:9px 20px; border-radius:999px; border:1.5px solid var(--qi-border); color:var(--qi-ink-muted); font-size:14px; text-decoration:none; transition:all .2s; }
.action-sec:hover { border-color:var(--qi-primary); color:var(--qi-primary); }

/* 骨架屏 */
.skeleton-row { display:flex; gap:1rem; }
.skeleton-card { flex:1; height:110px; border-radius:16px; background:linear-gradient(90deg,var(--qi-bg-muted) 25%,var(--qi-bg-card) 50%,var(--qi-bg-muted) 75%); background-size:200% 100%; animation:shimmer 1.4s infinite; }
@keyframes shimmer { 0%{background-position:200% 0}100%{background-position:-200% 0} }

/* 统计卡片 */
.stat-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:1rem; }
.stat-card { position:relative; overflow:hidden; background:var(--qi-bg-card); border:1px solid var(--qi-border); border-radius:16px; padding:1.4rem 1.25rem 1.1rem; transition:transform .2s,box-shadow .2s; }
.stat-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,var(--c1),var(--c2)); border-radius:16px 16px 0 0; }
.stat-card:hover { transform:translateY(-3px); box-shadow:0 8px 24px var(--qi-shadow); }
.sc-icon { font-size:20px; margin-bottom:.45rem; }
.sc-num { font-size:30px; font-weight:800; line-height:1; margin-bottom:.2rem; background:linear-gradient(135deg,var(--c1),var(--c2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.sc-label { font-size:13px; color:var(--qi-ink); font-weight:500; }
.sc-sub { font-size:11px; color:var(--qi-ink-light); margin-top:.2rem; }

/* 图表行 */
.charts-row { display:grid; grid-template-columns:1fr 1fr 220px; gap:1rem; }
.chart-card { background:var(--qi-bg-card); border:1px solid var(--qi-border); border-radius:16px; padding:1.25rem; }
.chart-card--pie { display:flex; flex-direction:column; }
.chart-hd { display:flex; align-items:center; gap:.6rem; margin-bottom:.5rem; }
.chart-title { font-size:13px; font-weight:600; color:var(--qi-ink); }
.chart-badge { font-size:11px; padding:2px 8px; border-radius:999px; background:rgba(255,140,90,.1); color:var(--qi-primary); }

/* ECharts 容器 */
.echart { width:100%; height:180px; }
.echart--pie { height:200px; flex:1; }
.echart--bar { width:100%; height:160px; }

/* 通用面板 */
.panel { background:var(--qi-bg-card); border:1px solid var(--qi-border); border-radius:16px; padding:1.25rem; }
.panel-hd { display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem; }
.panel-title { font-size:14px; font-weight:600; color:var(--qi-ink); }
.panel-sub { font-size:12px; color:var(--qi-ink-light); }
.panel-link { font-size:12px; color:var(--qi-primary); text-decoration:none; }
.panel-link:hover { text-decoration:underline; }
.panel-empty { padding:2rem; text-align:center; font-size:13px; color:var(--qi-ink-light); }

/* 最近文章 */
.recent-list { display:flex; flex-direction:column; }
.recent-row { display:flex; align-items:center; gap:1rem; padding:.75rem 0; border-bottom:1px solid var(--qi-border); }
.recent-row:last-child { border-bottom:none; padding-bottom:0; }
.rr-left { flex:1; min-width:0; }
.rr-title { display:block; font-size:14px; color:var(--qi-ink); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.rr-date { font-size:12px; color:var(--qi-ink-light); }
.rr-views { font-size:12px; color:var(--qi-ink-muted); flex-shrink:0; }
.rr-actions { display:flex; gap:.5rem; flex-shrink:0; }
.rr-btn { font-size:12px; font-weight:500; padding:4px 12px; border-radius:6px; border:1px solid var(--qi-border); background:transparent; color:var(--qi-ink-muted); text-decoration:none; cursor:pointer; transition:all .15s; }
.rr-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); }
.rr-btn--view { color:var(--qi-ink-light); }

@media (max-width:1100px) {
  .charts-row { grid-template-columns:1fr 1fr; }
  .chart-card--pie { grid-column:1 / -1; flex-direction:row; align-items:center; gap:1rem; }
  .echart--pie { height:160px; }
}
@media (max-width:900px) {
  .stat-grid { grid-template-columns:repeat(3,1fr); }
  .charts-row { grid-template-columns:1fr; }
  .chart-card--pie { grid-column:1; flex-direction:column; }
}
@media (max-width:600px) {
  .stat-grid { grid-template-columns:1fr 1fr; }
  .welcome-banner { flex-direction:column; gap:1rem; align-items:flex-start; }
}
</style>
