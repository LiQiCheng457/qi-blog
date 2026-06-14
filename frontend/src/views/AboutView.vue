<script setup lang="ts">
import { RouterLink } from 'vue-router'
import QiMascot from '@/components/QiMascot.vue'
import ScrollReveal from '@/components/ScrollReveal.vue'

const nameToAnchor = (name: string) => name.replace(/[\s/]+/g, '-')

const profileFacts = [
  { label: '昵称', value: '祁' },
  { label: '方向', value: '前端开发 / 全栈学习' },
  { label: '当前', value: '打磨个人博客与后台系统' },
  { label: '偏好', value: '清爽界面、稳定工程、可维护设计' },
]

const contactLinks = [
  { label: 'GitHub', value: 'https://github.com/LiQiCheng457', href: 'https://github.com/LiQiCheng457', isUrl: true, external: true },
  { label: 'Email', value: '3054109439@qq.com', href: 'mailto:3054109439@qq.com' },
  { label: 'Blog', value: '起风了', href: '/' },
]

const skillGroups = [
  {
    title: 'Frontend',
    items: ['Vue 3', 'TypeScript', 'Vite', 'UnoCSS', 'Pinia', 'Vue Router'],
  },
  {
    title: 'Backend',
    items: ['FastAPI', 'Python', 'SQLModel', 'asyncpg', 'REST API', 'JWT'],
  },
  {
    title: 'Database & Tools',
    items: ['PostgreSQL', 'Markdown', 'Git', 'Figma', 'ECharts', 'Highlight.js'],
  },
]

const nowDoing = [
  '把「起风了」从作品集博客继续升级成完整的个人内容系统',
  '完善文章、项目、评论、用户资料和后台管理这些基础能力',
  '练习把设计系统、交互细节和工程结构放到同一个节奏里',
]

const pinnedProjects = [
  {
    name: '新能源功率预测可视化大屏',
    desc: '基于 Vue 3、Three.js、ECharts 与 PatchTST 的新能源功率预测可视化平台，融合 3D 场景、地图态势和光伏功率预测数据。',
    stack: ['Vue 3', 'Three.js', 'ECharts', 'Python'],
  },
  {
    name: "Light Painting Newton's Rings",
    desc: '基于 PyQt5 与 Matplotlib 的牛顿环干涉仿真与分析工具，用公式、示意图、动态曲线和参数控制帮助理解明暗环变化规律。',
    stack: ['Python', 'PyQt5', 'Matplotlib', 'NumPy'],
  },
  {
    name: '光学仿真实验 / 瑕疵检测平台',
    desc: '基于 Vue 3 + Flask 的物理实验综合 Web 应用，覆盖波动光学仿真、虚拟实验导航、劈尖干涉瑕疵模拟和智能问答。',
    stack: ['Vue 3', 'Flask', 'ECharts', 'DeepSeek'],
  },
]

const timeline = [
  { year: '2026', title: '个人博客系统', desc: '搭建「起风了」个人博客，把作品、文章、后台和水豚 IP 串起来。' },
  { year: '2025', title: '全栈能力补齐', desc: '深入学习 Vue 3 Composition API 与 FastAPI 异步后端，开始关注接口设计。' },
  { year: '2024', title: '前端工程化', desc: '系统学习设计系统、组件拆分、路由状态管理和页面体验优化。' },
  { year: '2023', title: '工具与脚本', desc: '从 Python 小工具开始，把重复的事情交给代码处理。' },
]

</script>

<template>
  <div class="about-page">
    <div class="about-shell">
      <div class="profile-column">
        <aside class="profile-card" aria-label="个人资料">
          <div class="profile-hero">
            <QiMascot state="think" size="small" />
          </div>

          <div class="profile-heading">
            <h1>祁</h1>
            <p>Frontend Developer / Full-stack Learner</p>
          </div>

          <p class="profile-bio">
            喜欢在有风的下午写代码，也喜欢把工具做得清爽、稳定、刚刚好。
          </p>

          <dl class="fact-list">
            <div v-for="fact in profileFacts" :key="fact.label" class="fact-item">
              <dt>{{ fact.label }}</dt>
              <dd>{{ fact.value }}</dd>
            </div>
          </dl>

          <div class="contact-list">
            <a
              v-for="link in contactLinks"
              :key="link.label"
              :href="link.href"
              :target="link.external ? '_blank' : undefined"
              :rel="link.external ? 'noopener noreferrer' : undefined"
              class="contact-link"
            >
              <span>{{ link.label }}</span>
              <strong :class="{ 'contact-url': link.isUrl }">{{ link.value }}</strong>
            </a>
          </div>
        </aside>
      </div>

      <div class="readme-column">
        <ScrollReveal>
          <section class="readme-block intro-block">
            <div class="readme-title-row">
              <div>
                <h2>嗨，我是祁</h2>
              </div>
            </div>

            <p class="lead">
              我正在把「起风了」做成一个既能展示作品，也能沉淀文章和开发记录的个人博客系统。
              目前主要使用 Vue 3 做前端，用 FastAPI 和 PostgreSQL 处理后端与数据。
            </p>

            <div class="readme-divider"></div>

            <div class="readme-grid">
              <div class="readme-note">
                <span class="note-label">Now</span>
                <p>打磨博客前台体验、后台管理、文章编辑、评论和用户资料。</p>
              </div>
              <div class="readme-note">
                <span class="note-label">Focus</span>
                <p>前端工程化、组件设计、接口联调、内容系统和有温度的交互。</p>
              </div>
            </div>
          </section>
        </ScrollReveal>

        <ScrollReveal :delay="100">
          <section class="readme-block">
            <h2>正在做什么</h2>
            <ul class="doing-list">
              <li v-for="item in nowDoing" :key="item">{{ item }}</li>
            </ul>
          </section>
        </ScrollReveal>

        <ScrollReveal :delay="150">
          <section class="readme-block">
            <h2>技术栈</h2>
            <div class="skill-matrix">
              <div v-for="group in skillGroups" :key="group.title" class="skill-group">
                <h3>{{ group.title }}</h3>
                <div class="skill-tags">
                  <span v-for="skill in group.items" :key="skill" class="skill-tag">{{ skill }}</span>
                </div>
              </div>
            </div>
          </section>
        </ScrollReveal>

        <ScrollReveal :delay="200">
          <section class="readme-block">
            <h2>精选项目</h2>
            <div class="pinned-grid">
              <RouterLink
                v-for="project in pinnedProjects"
                :key="project.name"
                :to="`/projects#${nameToAnchor(project.name)}`"
                class="pinned-card"
              >
                <h3>{{ project.name }}</h3>
                <p>{{ project.desc }}</p>
                <div class="project-stack">
                  <span v-for="tech in project.stack" :key="tech">{{ tech }}</span>
                </div>
              </RouterLink>
            </div>
          </section>
        </ScrollReveal>

        <ScrollReveal :delay="300">
          <section class="readme-block">
            <h2>成长时间线</h2>
            <div class="timeline">
              <article v-for="item in timeline" :key="item.year" class="timeline-item">
                <span class="timeline-year">{{ item.year }}</span>
                <div>
                  <h3>{{ item.title }}</h3>
                  <p>{{ item.desc }}</p>
                </div>
              </article>
            </div>
          </section>
        </ScrollReveal>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about-page {
  min-height: 100vh;
  padding-top: 88px;
  background:
    radial-gradient(circle at 16% 8%, rgba(255, 209, 102, 0.18), transparent 26%),
    linear-gradient(160deg, var(--qi-bg) 0%, rgba(168, 216, 192, 0.08) 100%);
}

.about-shell {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  gap: 2rem;
  width: min(1560px, calc(100vw - 6rem));
  max-width: none;
  margin: 0 auto;
  padding: 3rem 1.5rem 5rem;
}

.profile-column {
  align-self: start;
  position: sticky;
  top: 88px;
  max-height: calc(100vh - 104px);
  overflow: visible;
  /* 确保 z 轴层叠不被右侧内容遮盖 */
  z-index: 1;
}

.profile-card,
.readme-block {
  border: 1px solid var(--qi-border);
  background: rgba(255, 248, 240, 0.72);
  box-shadow: 0 8px 24px var(--qi-shadow);
  backdrop-filter: blur(12px);
}

.profile-card {
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 104px);
  overflow: hidden;
  padding: 1rem;
}

.profile-hero {
  display: flex;
  justify-content: center;
  align-items: center;
  height: clamp(132px, 22vh, 190px);
  flex-shrink: 0;
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(255, 209, 102, 0.18), rgba(168, 216, 192, 0.18));
  overflow: hidden;
}

.profile-heading {
  margin-top: 0.85rem;
}

.profile-heading h1 {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(26px, 3.6vh, 34px);
  font-weight: 600;
  color: var(--qi-ink);
  line-height: 1.25;
}

.profile-heading p,
.profile-bio,
.fact-item dd,
.contact-link strong,
.readme-note p,
.doing-list,
.pinned-card p,
.timeline-item p {
  color: var(--qi-ink-muted);
}

.profile-heading p {
  font-size: 14px;
}

.profile-bio {
  margin-top: 0.65rem;
  font-size: 13px;
  line-height: 1.65;
}

.fact-list {
  display: grid;
  gap: 0.55rem;
  margin-top: 0.9rem;
}

.fact-item {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 0.75rem;
  font-size: 13px;
}

.fact-item dt {
  color: var(--qi-primary);
  font-weight: 700;
}

.fact-item dd {
  line-height: 1.6;
}

.contact-list {
  display: grid;
  gap: 0.25rem;
  margin-top: 0.8rem;
}

.contact-link {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.48rem 0;
  border-top: 1px solid var(--qi-border);
  text-decoration: none;
  font-size: 13px;
}

.contact-link span {
  color: var(--qi-ink);
  font-weight: 700;
}

.contact-link strong {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.contact-link strong.contact-url {
  color: var(--qi-primary);
  text-decoration: underline;
  text-underline-offset: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
}

.contact-link:hover strong.contact-url {
  color: var(--qi-soft);
}

.readme-column {
  display: grid;
  gap: 1rem;
  min-width: 0;
}

.readme-block {
  border-radius: 12px;
  padding: 1.5rem;
}

.intro-block {
  padding: 1.75rem;
}

.readme-title-row,
.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.section-heading span,
.note-label {
  color: var(--qi-primary);
  font-size: 12px;
  font-weight: 700;
}

.readme-block h2 {
  font-family: 'Noto Serif SC', serif;
  font-size: 26px;
  font-weight: 600;
  color: var(--qi-ink);
  line-height: 1.35;
}

.lead {
  margin-top: 1.25rem;
  color: var(--qi-ink);
  font-size: 16px;
  line-height: 1.9;
}

.readme-divider {
  height: 1px;
  margin: 1.35rem 0;
  background: var(--qi-border);
}

.readme-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.readme-note {
  padding: 1rem;
  border: 1px solid var(--qi-border);
  border-radius: 10px;
  background: var(--qi-bg-muted);
}

.readme-note p {
  margin-top: 0.35rem;
  font-size: 14px;
  line-height: 1.7;
}

.doing-list {
  display: grid;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-left: 1.25rem;
  font-size: 15px;
}

.doing-list li::marker {
  color: var(--qi-primary);
}

.skill-matrix {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
}

.skill-group {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 1rem;
  align-items: start;
  padding-top: 1rem;
  border-top: 1px solid var(--qi-border);
}

.skill-group:first-child {
  padding-top: 0;
  border-top: 0;
}

.skill-group h3,
.pinned-card h3,
.timeline-item h3 {
  color: var(--qi-ink);
  font-size: 15px;
  font-weight: 700;
}

.skill-tags,
.project-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag,
.project-stack span {
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.skill-tag {
  padding: 0.35rem 0.7rem;
  border: 1px solid var(--qi-border);
  color: var(--qi-ink);
  background: var(--qi-bg-card);
}

.pinned-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;
  margin-top: 1rem;
}

.pinned-card {
  display: block;
  min-height: 172px;
  padding: 1rem;
  border: 1px solid var(--qi-border);
  border-radius: 10px;
  background: var(--qi-bg-muted);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
  color: inherit;
}

.pinned-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px var(--qi-shadow);
}

.pinned-card p {
  margin: 0.6rem 0 1rem;
  font-size: 13px;
  line-height: 1.7;
}

.project-stack span {
  padding: 0.2rem 0.55rem;
  color: #5a8f78;
  background: rgba(168, 216, 192, 0.26);
}


.timeline {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
  position: relative;
}

.timeline-item {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--qi-border);
}

.timeline-item:first-child {
  padding-top: 0;
  border-top: 0;
}

.timeline-year {
  color: var(--qi-primary);
  font-size: 14px;
  font-weight: 800;
}

.timeline-item p {
  margin-top: 0.35rem;
  font-size: 14px;
  line-height: 1.7;
}

:global([data-theme="dark"] .profile-card),
:global([data-theme="dark"] .readme-block) {
  background: rgba(36, 30, 24, 0.8);
}

@media (min-width: 1280px) {
  .about-shell {
    grid-template-columns: 360px minmax(0, 1fr);
    gap: 2.25rem;
  }

  .readme-block {
    padding: 1.75rem;
  }

  .intro-block {
    padding: 2rem;
  }
}

@media (min-width: 1680px) {
  .about-shell {
    width: min(1660px, calc(100vw - 8rem));
    grid-template-columns: 380px minmax(0, 1fr);
    gap: 2.5rem;
  }
}

@media (max-width: 960px) {
  .about-shell {
    grid-template-columns: 1fr;
    width: min(100%, 760px);
  }

  .profile-column {
    position: static;
    max-height: none;
  }

  .profile-card {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 1.25rem;
    align-items: center;
    max-height: none;
    overflow: visible;
  }

  .profile-hero {
    height: 200px;
  }

  .profile-heading,
  .profile-bio,
  .fact-list,
  .contact-list {
    grid-column: 2;
  }
}

@media (max-width: 768px) {
  .about-page {
    padding-top: 72px;
  }

  .about-shell {
    padding: 2rem 1rem 4rem;
  }

  .profile-card {
    display: block;
    border-radius: 14px;
  }

  .profile-hero {
    min-height: 180px;
  }

  .readme-block,
  .intro-block {
    padding: 1.15rem;
  }

  .readme-title-row,
  .section-heading {
    display: grid;
  }

  .readme-grid,
  .pinned-grid {
    grid-template-columns: 1fr;
  }

  .skill-group,
  .timeline-item {
    grid-template-columns: 1fr;
    gap: 0.45rem;
  }

}
</style>
