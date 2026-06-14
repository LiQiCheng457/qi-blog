<script setup lang="ts">
import type { Project } from '@/types'

withDefaults(defineProps<{
  project: Project
  variant?: string
}>(), {
  variant: 'standard',
})

const categoryLabel: Record<string, string> = {
  frontend: '前端', backend: '后端', design: '设计', fullstack: '全栈',
  前端: '前端', 后端: '后端', 全栈: '全栈', 设计: '设计', 工具: '工具',
  'QT应用': 'QT 应用',
}

const isDownload = (link?: string) => !!link && link.endsWith('.zip')
</script>

<template>
  <article class="project-card" :class="`project-card--${variant}`">
    <!-- 项目封面 -->
    <div class="project-cover">
      <img v-if="project.cover" :src="project.cover" :alt="`${project.name} 项目预览`" class="project-cover-img" />
      <span class="project-category-badge">{{ categoryLabel[project.category] }}</span>
    </div>

    <div class="project-body">
      <div class="project-heading">
        <h3 class="project-name">{{ project.name }}</h3>
        <span v-if="project.status === 'active'" class="project-status">进行中</span>
        <span v-else-if="project.status === 'completed'" class="project-status">已完成</span>
      </div>
      <p class="project-desc">{{ project.description }}</p>

      <ul v-if="project.highlights?.length" class="project-highlights">
        <li v-for="item in project.highlights" :key="item">{{ item }}</li>
      </ul>

      <div class="project-stack">
        <span v-for="tech in project.techStack" :key="tech" class="stack-tag">{{ tech }}</span>
      </div>

      <div class="project-links">
        <a
          v-if="project.link && !isDownload(project.link)"
          :href="project.link"
          class="project-btn project-btn--primary"
          target="_blank"
        >查看 →</a>
        <a
          v-if="isDownload(project.link)"
          :href="project.link"
          class="project-btn project-btn--download"
          download
        >⬇ 下载程序</a>
        <a v-if="project.githubUrl" :href="project.githubUrl" class="project-btn" target="_blank">
          GitHub
        </a>
      </div>
    </div>

    <!-- hover 水豚贴纸 -->
    <div class="project-sticker">🐾</div>
  </article>
</template>

<style scoped>
.project-card {
  background: var(--qi-bg-card);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--qi-border);
  position: relative;
  display: grid;
  grid-template-columns: minmax(360px, 46%) minmax(0, 1fr);
  min-height: 320px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  cursor: default;
}

.project-card--side-right {
  grid-template-columns: minmax(0, 1fr) minmax(360px, 46%);
}

.project-card--side-right .project-cover {
  order: 2;
}

.project-card--side-right .project-body {
  order: 1;
}

.project-card--stack {
  display: block;
  min-height: 0;
}

.project-card--stack .project-cover {
  height: clamp(260px, 34vw, 430px);
  min-height: 0;
}

.project-card--stack .project-body {
  min-height: 260px;
  justify-content: flex-start;
}

.project-card--stack .project-highlights {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  padding-left: 0;
  list-style-position: inside;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(58, 42, 26, 0.08);
}

.project-card:hover .project-sticker {
  opacity: 1;
  transform: translate(0, 0);
}

.project-cover {
  height: 100%;
  min-height: 320px;
  background: linear-gradient(135deg, rgba(255, 140, 90, 0.15), rgba(168, 216, 192, 0.2));
  display: flex;
  align-items: flex-end;
  padding: 0.75rem;
  position: relative;
  overflow: hidden;
}

.project-cover-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.project-card:hover .project-cover-img {
  transform: scale(1.03);
}

.project-category-badge {
  position: relative;
  z-index: 1;
  font-size: 12px;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(255, 248, 240, 0.9);
  color: var(--qi-ink-muted);
}

.project-body {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1.5rem;
}

.project-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.project-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 23px;
  font-weight: 600;
  color: var(--qi-ink);
  line-height: 1.35;
}

.project-status {
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(255, 140, 90, 0.1);
  color: var(--qi-primary);
  font-size: 11px;
  font-weight: 700;
}

.project-desc {
  font-size: 15px;
  color: var(--qi-ink-muted);
  line-height: 1.7;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-highlights {
  display: grid;
  gap: 0.4rem;
  margin: -0.2rem 0 1rem;
  padding-left: 1rem;
  color: var(--qi-ink-muted);
  font-size: 12.5px;
  line-height: 1.55;
}

.project-highlights li::marker {
  color: var(--qi-primary);
}

.project-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.stack-tag {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(168, 216, 192, 0.25);
  color: #5A9E82;
}

.project-links {
  display: flex;
  gap: 0.5rem;
}

.project-btn {
  font-size: 13px;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: 999px;
  text-decoration: none;
  border: 1.5px solid var(--qi-border);
  color: var(--qi-ink-muted);
  transition: all 0.2s;
}

.project-btn:hover {
  border-color: var(--qi-primary);
  color: var(--qi-primary);
}

.project-btn--primary {
  background: var(--qi-primary);
  border-color: var(--qi-primary);
  color: white;
}

.project-btn--primary:hover {
  opacity: 0.88;
  color: white;
}

.project-btn--download {
  background: var(--qi-bg-muted);
  border-color: var(--qi-border);
  color: var(--qi-ink);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.project-btn--download:hover {
  background: var(--qi-primary);
  border-color: var(--qi-primary);
  color: white;
}

.project-sticker {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  font-size: 22px;
  opacity: 0;
  transform: translate(4px, 4px);
  transition: opacity 0.25s, transform 0.25s;
  pointer-events: none;
}

@media (max-width: 1100px) {
  .project-card {
    grid-template-columns: minmax(300px, 44%) minmax(0, 1fr);
  }

  .project-card--side-right {
    grid-template-columns: minmax(0, 1fr) minmax(300px, 44%);
  }

  .project-card--stack .project-highlights {
    grid-template-columns: 1fr;
    padding-left: 1rem;
    list-style-position: outside;
  }
}

@media (max-width: 900px) {
  .project-card,
  .project-card--side-right,
  .project-card--stack {
    display: block;
    min-height: 0;
  }

  .project-card--side-right .project-cover,
  .project-card--side-right .project-body {
    order: initial;
  }

  .project-cover,
  .project-card--stack .project-cover {
    height: 220px;
    min-height: 0;
  }

  .project-card--stack .project-body {
    min-height: 0;
  }

  .project-card--stack .project-highlights {
    grid-template-columns: 1fr;
    padding-left: 1rem;
    list-style-position: outside;
  }

  .project-name {
    font-family: 'Inter', sans-serif;
    font-size: 18px;
  }
}
</style>
