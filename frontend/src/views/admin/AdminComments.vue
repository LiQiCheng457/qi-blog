<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminApi } from '@/api/admin'
import type { AdminComment } from '@/api/admin'
import { assetUrl } from '@/utils/assets'

const route  = useRoute()
const router = useRouter()

const comments = ref<AdminComment[]>([])
const loading  = ref(true)
const search   = ref('')
const error    = ref('')
const slugFilter = ref('全部')

// 从路由 query 读取用户筛选
const filterUserId   = computed(() => route.query.userId   ? Number(route.query.userId)      : undefined)
const filterUsername = computed(() => route.query.username ? String(route.query.username)    : undefined)

const slugOptions = computed(() => {
  const set = new Set(comments.value.map(c => c.post_slug))
  return ['全部', ...Array.from(set).sort()]
})

const filtered = computed(() => {
  let list = comments.value
  if (slugFilter.value !== '全部') list = list.filter(c => c.post_slug === slugFilter.value)
  const q = search.value.trim().toLowerCase()
  if (q) list = list.filter(c =>
    c.content.toLowerCase().includes(q) || c.username.toLowerCase().includes(q)
  )
  return list
})

async function load() {
  loading.value    = true
  error.value      = ''
  slugFilter.value = '全部'
  try {
    comments.value = await adminApi.listComments(filterUserId.value)
  } catch (e: any) {
    error.value = e.message ?? '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)

// 当路由 query 变化时重新加载（从用户管理跳入）
watch(() => route.query.userId, load)

function clearUserFilter() {
  router.push({ name: 'admin-comments' })
}

function formatDate(s: string) {
  const d = new Date(s)
  return d.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

async function deleteComment(c: AdminComment) {
  if (!confirm(`确定删除「${c.username}」的这条评论？`)) return
  try {
    await adminApi.deleteComment(c.id)
    comments.value = comments.value.filter(x => x.id !== c.id)
  } catch (e: any) {
    alert(e.message ?? '删除失败')
  }
}
</script>

<template>
  <div class="admin-comments">
    <div class="page-header">
      <div>
        <h1 class="page-title">评论管理</h1>
        <p class="page-sub">共 {{ comments.length }} 条评论</p>
      </div>
    </div>

    <!-- 用户筛选 chip -->
    <div v-if="filterUsername" class="filter-chip-bar">
      <div class="filter-chip">
        <span>正在查看：<strong>{{ filterUsername }}</strong> 的评论</span>
        <button class="chip-clear" @click="clearUserFilter" title="取消筛选">×</button>
      </div>
    </div>

    <div class="toolbar">
      <select v-model="slugFilter" class="slug-select">
        <option v-for="s in slugOptions" :key="s" :value="s">
          {{ s === '全部' ? '全部文章' : s }}
        </option>
      </select>
      <input v-model="search" class="search-input" type="text" placeholder="搜索评论内容或用户名…" />
    </div>

    <div v-if="error" class="err-msg">{{ error }}</div>
    <div v-else-if="loading" class="empty">加载中…</div>
    <div v-else-if="filtered.length === 0" class="empty">没有匹配的评论</div>
    <div v-else class="comment-list">
      <div v-for="c in filtered" :key="c.id" class="comment-card">
        <!-- 头部：用户信息 + 操作 -->
        <div class="card-header">
          <div class="user-block">
            <div class="user-avatar">
              <img v-if="c.avatar" :src="assetUrl(c.avatar)" :alt="c.username" />
              <span v-else class="avatar-fallback">{{ c.username[0] }}</span>
            </div>
            <div class="user-meta">
              <div class="user-name-line">
                <span class="username">{{ c.username }}</span>
                <span v-if="c.role === 'admin'" class="admin-tag">管理员</span>
              </div>
              <span class="comment-date">{{ formatDate(c.created_at) }}</span>
            </div>
          </div>
          <div class="card-actions">
            <span class="slug-chip">{{ c.post_slug }}</span>
            <button class="del-btn" @click="deleteComment(c)">删除</button>
          </div>
        </div>

        <!-- 评论内容 -->
        <p class="comment-content">{{ c.content }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-comments { width: 100%; }
.page-header { margin-bottom:1rem; }
.page-title { font-family:'Noto Serif SC',serif; font-size:28px; font-weight:500; color:var(--qi-ink); margin-bottom:.25rem; }
.page-sub { font-size:13px; color:var(--qi-ink-muted); }

/* 用户筛选 chip */
.filter-chip-bar { margin-bottom:1rem; }
.filter-chip {
  display:inline-flex; align-items:center; gap:.6rem;
  background:rgba(255,140,90,.1); border:1px solid rgba(255,140,90,.3);
  color:var(--qi-primary); border-radius:999px; padding:5px 10px 5px 14px;
  font-size:13px;
}
.filter-chip strong { font-weight:600; }
.chip-clear {
  all:unset; cursor:pointer; font-size:16px; line-height:1;
  width:20px; height:20px; display:flex; align-items:center; justify-content:center;
  border-radius:50%; color:var(--qi-primary); opacity:.7; transition:opacity .15s;
}
.chip-clear:hover { opacity:1; background:rgba(255,140,90,.15); }

.toolbar { display:flex; gap:.75rem; margin-bottom:1.25rem; flex-wrap:wrap; }
.slug-select, .search-input {
  padding:8px 12px; border-radius:8px; border:1.5px solid var(--qi-border);
  background:var(--qi-bg); font-size:13.5px; color:var(--qi-ink);
  outline:none; font-family:inherit; transition:border-color .15s;
}
.slug-select { min-width:160px; }
.search-input { flex:1; min-width:180px; }
.slug-select:focus, .search-input:focus { border-color:var(--qi-primary); }

.err-msg { color:#e05050; font-size:13.5px; }
.empty { color:var(--qi-ink-light); font-size:14px; padding:2rem 0; }

/* 评论卡片 */
.comment-list { display:flex; flex-direction:column; gap:.6rem; }
.comment-card {
  background:var(--qi-bg-card); border:1px solid var(--qi-border);
  border-radius:12px; padding:1rem 1.1rem; display:flex; flex-direction:column; gap:.7rem;
  transition:border-color .15s;
}
.comment-card:hover { border-color:var(--qi-border-muted, rgba(var(--qi-ink-rgb, 0,0,0),.15)); }

.card-header { display:flex; align-items:flex-start; justify-content:space-between; gap:.75rem; flex-wrap:wrap; }

.user-block { display:flex; align-items:center; gap:.6rem; }
.user-avatar { width:32px; height:32px; border-radius:50%; overflow:hidden; border:1px solid var(--qi-border); flex-shrink:0; }
.user-avatar img { width:100%; height:100%; object-fit:cover; }
.avatar-fallback {
  width:100%; height:100%; display:flex; align-items:center; justify-content:center;
  background:var(--qi-bg-muted); font-size:12px; font-weight:600; color:var(--qi-primary);
}
.user-meta { display:flex; flex-direction:column; gap:.15rem; }
.user-name-line { display:flex; align-items:center; gap:.4rem; }
.username { font-size:13.5px; font-weight:500; color:var(--qi-ink); }
.admin-tag { font-size:10px; font-weight:600; padding:1px 6px; border-radius:999px; background:rgba(255,140,90,.12); color:var(--qi-primary); }
.comment-date { font-size:11.5px; color:var(--qi-ink-light); }

.card-actions { display:flex; align-items:center; gap:.5rem; flex-shrink:0; }
.slug-chip {
  font-size:11.5px; color:var(--qi-ink-muted); background:var(--qi-bg);
  border:1px solid var(--qi-border); border-radius:6px; padding:2px 8px;
  white-space:nowrap; max-width:200px; overflow:hidden; text-overflow:ellipsis;
}
.del-btn {
  font-size:12px; padding:4px 12px; border-radius:6px;
  border:none; background:transparent; color:#e05050; cursor:pointer; transition:background .15s;
}
.del-btn:hover { background:rgba(224,80,80,.08); }

.comment-content {
  font-size:14px; color:var(--qi-ink-muted); line-height:1.7;
  white-space:pre-wrap; word-break:break-all; margin:0;
  padding:.6rem .75rem; background:var(--qi-bg); border-radius:8px;
}

@media(max-width:540px){
  .card-header { flex-direction:column; }
  .card-actions { align-self:flex-end; }
  .slug-chip { max-width:140px; }
}
</style>
