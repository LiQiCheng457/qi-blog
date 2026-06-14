<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useBlogStore } from '@/stores/blog'
import QiMascot from '@/components/QiMascot.vue'
import ScrollReveal from '@/components/ScrollReveal.vue'
import PostCard from '@/components/PostCard.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'

const store = useBlogStore()
const searchQuery = ref('')
const activeTag   = ref('')
const page        = ref(1)
const PAGE_SIZE   = 8

onMounted(() => store.fetchPosts())

const allTags = computed(() => store.getAllTags())

const filteredPosts = computed(() => {
  let posts = store.posts
  if (activeTag.value) posts = posts.filter(p => p.tags.includes(activeTag.value))
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    posts = posts.filter(p => p.title.toLowerCase().includes(q) || p.summary.toLowerCase().includes(q))
  }
  return posts
})

const totalPages  = computed(() => Math.max(1, Math.ceil(filteredPosts.value.length / PAGE_SIZE)))
const pagedPosts  = computed(() => filteredPosts.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE))

// 过滤条件变化时重置页码
watch([searchQuery, activeTag], () => { page.value = 1 })

function toggleTag(tag: string) {
  activeTag.value = activeTag.value === tag ? '' : tag
}
function goPage(p: number) {
  page.value = p
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="blog-page">
    <div class="blog-inner">
      <div class="blog-header">
        <div class="header-text">
          <ScrollReveal>
            <h1 class="page-title">起风了，想写点什么</h1>
            <p class="page-subtitle">技术、设计、生活，以及那些有风的下午。</p>
          </ScrollReveal>
          <ScrollReveal :delay="100">
            <div class="search-wrap">
              <input v-model="searchQuery" type="search" placeholder="搜索文章…" class="search-input" />
            </div>
          </ScrollReveal>
          <ScrollReveal :delay="150">
            <div class="tag-filters">
              <button v-for="tag in allTags" :key="tag" class="tag-filter"
                :class="{ active: activeTag === tag }" @click="toggleTag(tag)">
                {{ tag }}
              </button>
            </div>
          </ScrollReveal>
        </div>
        <div class="header-mascot">
          <QiMascot state="singing" size="medium" />
        </div>
      </div>

      <!-- 骨架屏 -->
      <div v-if="store.loading" class="posts-list">
        <SkeletonCard v-for="i in 4" :key="i" />
      </div>

      <template v-else>
        <div class="posts-list">
          <ScrollReveal v-for="(post, i) in pagedPosts" :key="post.slug" :delay="i * 60">
            <PostCard :post="post" />
          </ScrollReveal>
          <div v-if="filteredPosts.length === 0" class="empty">没有找到相关文章，换个关键词试试？</div>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination">
          <button class="pg-btn" :disabled="page === 1" @click="goPage(page - 1)">‹</button>
          <button
            v-for="p in totalPages"
            :key="p"
            class="pg-btn"
            :class="{ active: p === page }"
            @click="goPage(p)"
          >{{ p }}</button>
          <button class="pg-btn" :disabled="page === totalPages" @click="goPage(page + 1)">›</button>
        </div>

        <!-- 文章数统计 -->
        <p v-if="filteredPosts.length > 0" class="post-count">
          共 {{ filteredPosts.length }} 篇文章
          <template v-if="totalPages > 1">· 第 {{ page }} / {{ totalPages }} 页</template>
        </p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.blog-page { min-height: 100vh; padding-top: 80px; background: var(--qi-bg); }
.blog-inner { max-width: 896px; min-height: calc(100vh - 80px); margin: 0 auto; padding: 4rem 1.5rem; }
.blog-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 2rem; margin-bottom: 3rem; }
.header-text { flex: 1; }
.page-title { font-family: 'Noto Serif SC', serif; font-size: 36px; font-weight: 500; color: var(--qi-ink); margin-bottom: .75rem; }
.page-subtitle { font-size: 15px; color: var(--qi-ink-muted); margin-bottom: 1.5rem; }
.search-wrap { margin-bottom: 1.25rem; }
.search-input { width: 100%; max-width: 400px; padding: 10px 16px; border-radius: 999px; border: 1.5px solid var(--qi-border); background: var(--qi-bg-card); font-size: 14px; color: var(--qi-ink); outline: none; transition: border-color .2s; }
.search-input:focus { border-color: var(--qi-primary); }
.search-input::placeholder { color: var(--qi-ink-light); }
.tag-filters { display: flex; flex-wrap: wrap; gap: .5rem; }
.tag-filter { font-size: 12px; font-weight: 500; padding: 4px 12px; border-radius: 999px; border: 1.5px solid var(--qi-border); background: transparent; color: var(--qi-ink-muted); cursor: pointer; transition: all .2s; }
.tag-filter:hover, .tag-filter.active { background: rgba(255,140,90,.12); border-color: var(--qi-primary); color: var(--qi-primary); }
.header-mascot { flex-shrink: 0; }
.posts-list { display: flex; flex-direction: column; gap: 1.5rem; }
.empty { text-align: center; padding: 4rem 0; color: var(--qi-ink-muted); }

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: .4rem;
  margin-top: 3rem;
}
.pg-btn {
  min-width: 36px; height: 36px;
  padding: 0 10px;
  border-radius: 8px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-card);
  color: var(--qi-ink-muted);
  font-size: 14px; font-weight: 500;
  cursor: pointer;
  transition: all .15s;
}
.pg-btn:hover:not(:disabled):not(.active) { border-color: var(--qi-primary); color: var(--qi-primary); }
.pg-btn.active { background: var(--qi-primary); color: white; border-color: var(--qi-primary); }
.pg-btn:disabled { opacity: .4; cursor: not-allowed; }

.post-count { text-align: center; margin-top: 1rem; font-size: 13px; color: var(--qi-ink-light); }

@media (max-width: 768px) {
  .blog-header { flex-direction: column; align-items: center; text-align: center; }
  .tag-filters { justify-content: center; }
  .search-input { max-width: 100%; }
}
</style>
