<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { wishesApi, type WishAdmin } from '@/api/wishes'

const wishes  = ref<WishAdmin[]>([])
const loading = ref(true)
const filter  = ref<'all' | 'user' | 'seed' | 'resonated'>('all')
const search  = ref('')

async function load() {
  loading.value = true
  try { wishes.value = await wishesApi.adminList() }
  finally { loading.value = false }
}
onMounted(load)

const filtered = computed(() => {
  let list = wishes.value
  if (filter.value === 'user')      list = list.filter(w => !w.is_seed)
  else if (filter.value === 'seed') list = list.filter(w =>  w.is_seed)
  else if (filter.value === 'resonated') list = list.filter(w => w.resonance_count > 0)
  const q = search.value.trim().toLowerCase()
  if (q) list = list.filter(w =>
    w.content.toLowerCase().includes(q) ||
    (w.username ?? '').toLowerCase().includes(q),
  )
  return list
})

const stats = computed(() => {
  const total = wishes.value.length
  const seed  = wishes.value.filter(w => w.is_seed).length
  const userCount = total - seed
  const totalReso = wishes.value.reduce((a, w) => a + w.resonance_count, 0)
  return { total, seed, userCount, totalReso }
})

async function delOne(w: WishAdmin) {
  if (!confirm(`确认删除这条愿望？\n\n"${w.content}"`)) return
  try {
    await wishesApi.adminDelete(w.id)
    wishes.value = wishes.value.filter(x => x.id !== w.id)
  } catch (e: any) {
    alert(e?.message ?? '删除失败')
  }
}

async function clearAll() {
  if (!confirm('确认清空所有用户愿望（保留种子愿望）？此操作不可撤销。')) return
  try {
    const res = await wishesApi.adminClear()
    alert(`已清空 ${res.cleared} 条用户愿望`)
    await load()
  } catch (e: any) {
    alert(e?.message ?? '清空失败')
  }
}

function fmtTime(s: string) {
  const d = new Date(s)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}
</script>

<template>
  <div class="admin-wishes">
    <header class="page-header">
      <div>
        <h1 class="page-title">许愿池管理</h1>
        <p class="page-sub">查看所有愿望及其被共鸣次数；可单条删除或清空用户愿望。</p>
      </div>
      <button class="danger-btn" @click="clearAll">清空用户愿望</button>
    </header>

    <!-- 统计 -->
    <div class="stat-row">
      <div class="stat-card">
        <span class="stat-label">总愿望</span>
        <span class="stat-num">{{ stats.total }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">用户投递</span>
        <span class="stat-num">{{ stats.userCount }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">种子愿望</span>
        <span class="stat-num">{{ stats.seed }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">共鸣总数</span>
        <span class="stat-num">{{ stats.totalReso }}</span>
      </div>
    </div>

    <!-- 过滤 + 搜索 -->
    <div class="tool-row">
      <div class="filter-pills">
        <button v-for="f in [
          { k: 'all',       label: '全部'   },
          { k: 'user',      label: '用户'   },
          { k: 'seed',      label: '种子'   },
          { k: 'resonated', label: '有共鸣' },
        ]" :key="f.k"
          class="pill" :class="{ active: filter === f.k }"
          @click="filter = (f.k as any)"
        >{{ f.label }}</button>
      </div>
      <input v-model="search" placeholder="搜索愿望或用户名…" class="search-input" />
    </div>

    <div v-if="loading" class="loading">加载中…</div>
    <div v-else-if="!filtered.length" class="empty">暂无愿望</div>

    <table v-else class="wish-table">
      <thead>
        <tr>
          <th class="col-id">#</th>
          <th class="col-content">愿望内容</th>
          <th class="col-user">投递者</th>
          <th class="col-reso">共鸣数</th>
          <th class="col-time">投递时间</th>
          <th class="col-action">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="w in filtered" :key="w.id">
          <td class="col-id">{{ w.id }}</td>
          <td class="col-content">
            <span v-if="w.is_seed" class="seed-tag">种子</span>
            {{ w.content }}
          </td>
          <td class="col-user">
            <span v-if="w.is_seed" class="muted">— 系统</span>
            <span v-else-if="w.username">{{ w.username }}</span>
            <span v-else class="muted">已注销</span>
          </td>
          <td class="col-reso">
            <span class="reso-num" :class="{ hot: w.resonance_count >= 5 }">{{ w.resonance_count }}</span>
          </td>
          <td class="col-time">{{ fmtTime(w.created_at) }}</td>
          <td class="col-action">
            <button class="del-btn" @click="delOne(w)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.admin-wishes { display: flex; flex-direction: column; gap: 1.25rem; }

.page-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 1rem;
}
.page-title { font-family: 'Noto Serif SC', serif; font-size: 28px; font-weight: 500; color: var(--qi-ink); margin: 0 0 .25rem; }
.page-sub { font-size: .85rem; color: var(--qi-ink-muted); margin: 0; }

.danger-btn {
  padding: .45rem 1rem; border-radius: 8px;
  border: 1.5px solid rgba(217, 79, 79, .3);
  background: none; color: #d94f4f;
  font-size: .85rem; cursor: pointer; transition: all .2s;
}
.danger-btn:hover { background: rgba(217, 79, 79, .08); border-color: #d94f4f; }

/* 统计卡片 */
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}
.stat-card {
  background: var(--qi-bg-card);
  border: 1px solid var(--qi-border);
  border-radius: 12px;
  padding: .875rem 1rem;
  display: flex; flex-direction: column; gap: .25rem;
}
.stat-label { font-size: .72rem; color: var(--qi-ink-muted); }
.stat-num   { font-size: 1.6rem; font-weight: 700; color: var(--qi-ink); font-variant-numeric: tabular-nums; }

/* 过滤 + 搜索 */
.tool-row {
  display: flex; align-items: center; gap: 1rem;
  flex-wrap: wrap;
}
.filter-pills { display: flex; gap: .375rem; }
.pill {
  padding: .35rem .75rem;
  border-radius: 999px;
  border: 1.5px solid var(--qi-border);
  background: none; color: var(--qi-ink-muted);
  font-size: .8rem; cursor: pointer; transition: all .2s;
}
.pill:hover { border-color: var(--qi-primary); color: var(--qi-primary); }
.pill.active {
  background: var(--qi-primary); border-color: var(--qi-primary); color: #fff;
}
.search-input {
  flex: 1; min-width: 180px; max-width: 320px;
  padding: .4rem .75rem;
  border-radius: 8px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-card);
  color: var(--qi-ink);
  font-size: .82rem; outline: none;
  transition: border-color .2s;
}
.search-input:focus { border-color: var(--qi-primary); }

/* 状态 */
.loading, .empty {
  padding: 2.5rem; text-align: center;
  color: var(--qi-ink-light); font-size: .9rem;
}

/* 表格 */
.wish-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: var(--qi-bg-card);
  border: 1px solid var(--qi-border);
  border-radius: 12px;
  overflow: hidden;
}
.wish-table th,
.wish-table td {
  padding: .65rem .875rem;
  text-align: left;
  font-size: .85rem;
  border-bottom: 1px solid var(--qi-border);
}
.wish-table th {
  background: var(--qi-bg-muted);
  font-size: .74rem; font-weight: 600;
  color: var(--qi-ink-muted);
  letter-spacing: .04em;
}
.wish-table tbody tr:last-child td { border-bottom: none; }
.wish-table tbody tr:hover { background: rgba(255,140,90,.03); }

.col-id { width: 50px; color: var(--qi-ink-light); font-variant-numeric: tabular-nums; }
.col-content { color: var(--qi-ink); }
.col-user { width: 120px; color: var(--qi-ink-muted); }
.col-reso { width: 80px; text-align: center; }
.col-time { width: 150px; color: var(--qi-ink-light); font-size: .76rem; font-variant-numeric: tabular-nums; }
.col-action { width: 80px; text-align: right; }

.seed-tag {
  display: inline-block;
  font-size: .62rem; font-weight: 600;
  padding: 1px 6px; border-radius: 999px;
  background: rgba(168, 216, 192, 0.2);
  color: #3a8a6a;
  margin-right: .375rem;
  vertical-align: middle;
}

.reso-num {
  font-weight: 700; font-variant-numeric: tabular-nums;
  color: var(--qi-ink-muted);
}
.reso-num.hot { color: var(--qi-primary); }

.muted { color: var(--qi-ink-light); }

.del-btn {
  font-size: .76rem;
  padding: .25rem .65rem;
  border-radius: 6px;
  border: 1px solid var(--qi-border);
  background: none; color: var(--qi-ink-muted);
  cursor: pointer; transition: all .15s;
}
.del-btn:hover { border-color: #d94f4f; color: #d94f4f; background: rgba(217, 79, 79, .06); }

@media (max-width: 768px) {
  .stat-row { grid-template-columns: repeat(2, 1fr); }
  .col-time { display: none; }
  .col-user { width: 80px; }
}
</style>
