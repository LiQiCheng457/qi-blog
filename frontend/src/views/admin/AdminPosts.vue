<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { postsApi } from '@/api/posts'
import type { Post } from '@/types'

const posts   = ref<Post[]>([])
const loading = ref(true)
const deleting = ref<string | null>(null)

async function load() {
  loading.value = true
  try { posts.value = await postsApi.list() } finally { loading.value = false }
}

onMounted(load)

async function deletePost(slug: string, title: string) {
  if (!confirm(`确定删除《${title}》？此操作不可撤销。`)) return
  deleting.value = slug
  try {
    await postsApi.delete(slug)
    posts.value = posts.value.filter(p => p.slug !== slug)
  } finally {
    deleting.value = null
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', { year:'numeric', month:'short', day:'numeric' })
}
</script>

<template>
  <div class="admin-posts">
    <div class="page-header">
      <h1 class="page-title">文章管理</h1>
      <RouterLink to="/admin/posts/new" class="new-btn">+ 写新文章</RouterLink>
    </div>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else class="posts-table">
      <div class="table-head">
        <span class="col-title">标题</span>
        <span class="col-tags">标签</span>
        <span class="col-date">发布日期</span>
        <span class="col-rt">阅读时间</span>
        <span class="col-actions">操作</span>
      </div>

      <div v-for="post in posts" :key="post.slug" class="table-row">
        <span class="col-title">
          <RouterLink :to="`/blog/${post.slug}`" target="_blank" class="post-title-link">
            {{ post.title }}
          </RouterLink>
        </span>
        <span class="col-tags">
          <span v-for="tag in post.tags.slice(0,2)" :key="tag" class="tag">{{ tag }}</span>
          <span v-if="post.tags.length > 2" class="tag-more">+{{ post.tags.length - 2 }}</span>
        </span>
        <span class="col-date">{{ formatDate(post.createdAt) }}</span>
        <span class="col-rt">{{ post.readingTime }} 分钟</span>
        <span class="col-actions">
          <RouterLink :to="`/admin/posts/${post.slug}/edit`" class="action-btn">编辑</RouterLink>
          <button class="action-btn delete"
            :disabled="deleting === post.slug"
            @click="deletePost(post.slug, post.title)">
            {{ deleting === post.slug ? '…' : '删除' }}
          </button>
        </span>
      </div>

      <div v-if="posts.length === 0" class="empty">还没有文章，去写第一篇吧！</div>
    </div>
  </div>
</template>

<style scoped>
.admin-posts { width:100%; }
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:2rem; }
.page-title { font-family:'Noto Serif SC',serif; font-size:28px; font-weight:500; color:var(--qi-ink); }
.new-btn { display:inline-block; padding:9px 20px; border-radius:999px; background:var(--qi-primary); color:white; font-size:14px; font-weight:500; text-decoration:none; }
.new-btn:hover { opacity:.88; }
.loading { color:var(--qi-ink-light); font-size:14px; }
.posts-table { background:var(--qi-bg-card); border:1px solid var(--qi-border); border-radius:14px; overflow:hidden; }
.table-head { display:grid; grid-template-columns:1fr 140px 110px 80px 100px; gap:.75rem; padding:.75rem 1.25rem; background:var(--qi-bg); border-bottom:1px solid var(--qi-border); font-size:12px; font-weight:600; color:var(--qi-ink-muted); text-transform:uppercase; letter-spacing:.04em; }
.table-row { display:grid; grid-template-columns:1fr 140px 110px 80px 100px; gap:.75rem; padding:.875rem 1.25rem; border-bottom:1px solid var(--qi-border); align-items:center; }
.table-row:last-child { border-bottom:none; }
.col-title { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.post-title-link { font-size:14px; color:var(--qi-ink); text-decoration:none; }
.post-title-link:hover { color:var(--qi-primary); }
.col-tags { display:flex; flex-wrap:wrap; gap:4px; }
.tag { font-size:11px; padding:2px 8px; border-radius:999px; background:rgba(255,140,90,.1); color:var(--qi-primary); }
.tag-more { font-size:11px; color:var(--qi-ink-light); }
.col-date,.col-rt { font-size:13px; color:var(--qi-ink-muted); }
.col-actions { display:flex; gap:.5rem; }
.action-btn { font-size:12px; font-weight:500; padding:4px 10px; border-radius:6px; border:1px solid var(--qi-border); background:transparent; color:var(--qi-ink-muted); cursor:pointer; text-decoration:none; transition:all .15s; }
.action-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); }
.action-btn.delete { color:#e05050; border-color:transparent; }
.action-btn.delete:hover { background:rgba(224,80,80,.08); border-color:#e05050; }
.action-btn:disabled { opacity:.5; cursor:not-allowed; }
.empty { padding:3rem; text-align:center; font-size:14px; color:var(--qi-ink-light); }
@media(max-width:700px){
  .table-head,.table-row{grid-template-columns:1fr auto;}
  .col-tags,.col-date,.col-rt{display:none;}
}
</style>
