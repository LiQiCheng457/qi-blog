<script setup lang="ts">
import type { Post } from '@/types'

defineProps<{ post: Post }>()

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <RouterLink :to="`/blog/${post.slug}`" class="post-card">
    <div class="post-meta">
      <time :datetime="post.createdAt" class="post-date">{{ formatDate(post.createdAt) }}</time>
      <span class="post-reading">· {{ post.readingTime }} 分钟</span>
    </div>
    <h3 class="post-title">{{ post.title }}</h3>
    <p class="post-summary">{{ post.summary }}</p>
    <div class="post-tags">
      <span v-for="tag in post.tags" :key="tag" class="post-tag">{{ tag }}</span>
    </div>
    <div class="post-mascot">🐾</div>
  </RouterLink>
</template>

<style scoped>
.post-card {
  display: block;
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--qi-border);
  text-decoration: none;
  color: inherit;
  position: relative;
  transition: transform 0.2s;
}

.post-card:last-child {
  border-bottom: none;
}

.post-card:hover {
  transform: translateX(4px);
}

.post-card:hover .post-mascot {
  opacity: 1;
  transform: translateY(-2px);
}

.post-meta {
  font-size: 13px;
  color: var(--qi-ink-light);
  margin-bottom: 0.5rem;
  font-family: 'Inter', sans-serif;
}

.post-date {
  font-size: 13px;
}

.post-reading {
  font-size: 13px;
}

.post-title {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 500;
  color: var(--qi-ink);
  margin-bottom: 0.5rem;
  line-height: 1.5;
  transition: color 0.2s;
}

.post-card:hover .post-title {
  color: var(--qi-primary);
}

.post-summary {
  font-size: 14px;
  color: var(--qi-ink-muted);
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.post-tag {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(255, 140, 90, 0.12);
  color: var(--qi-primary);
}

.post-mascot {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: 20px;
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s;
}
</style>
