<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useBlogStore } from '@/stores/blog'
import WindParticles from '@/components/WindParticles.vue'
import QiMascot from '@/components/QiMascot.vue'
import TypingText from '@/components/TypingText.vue'
import ScrollReveal from '@/components/ScrollReveal.vue'
import SectionTitle from '@/components/SectionTitle.vue'
import PostCard from '@/components/PostCard.vue'

const store = useBlogStore()
const featuredProjects = computed(() => store.getFeaturedProjects())
const primaryProject = computed(() => featuredProjects.value[0])
const secondaryProjects = computed(() => featuredProjects.value.slice(1, 3))
const recentPosts      = computed(() => store.posts.slice(0, 5))

function projectHref(project: { link?: string; githubUrl?: string }) {
  return project.link || project.githubUrl || '/projects'
}

onMounted(async () => {
  await Promise.all([store.fetchPosts(), store.fetchProjects()])
})
</script>

<template>
  <section class="hero">
    <WindParticles />
    <div class="hero-glow" aria-hidden="true"></div>
    <div class="hero-inner">
      <div class="hero-text">
        <h1 class="hero-title">
          <TypingText text="你好，我是祁" :delay="1200" :speed="80" />
        </h1>
        <p class="hero-subtitle">起风了，想写点什么</p>
        <div class="hero-ctas">
          <RouterLink to="/blog" class="cta-btn cta-btn--primary">看看我写了什么 →</RouterLink>
          <RouterLink to="/about" class="cta-btn">了解一下我 →</RouterLink>
        </div>
      </div>
      <div class="hero-mascot">
        <QiMascot state="wave" size="large" />
      </div>
    </div>
    <div class="scroll-hint" aria-hidden="true">↓</div>
  </section>

  <section class="section section--projects">
    <div class="section-inner">
      <ScrollReveal>
        <SectionTitle title="最近在做" subtitle="一些还在折腾的东西" />
      </ScrollReveal>
      <div v-if="store.loading" class="loading-tip">加载中…</div>
      <div v-else class="home-projects">
        <ScrollReveal v-if="primaryProject" :delay="80">
          <article class="featured-project">
            <a class="featured-project__media" :href="projectHref(primaryProject)" target="_blank">
              <img v-if="primaryProject.cover" :src="primaryProject.cover" :alt="`${primaryProject.name} 项目预览`" />
              <span class="project-badge">{{ primaryProject.category }}</span>
            </a>
            <div class="featured-project__body">
              <p class="project-kicker">Featured Project</p>
              <h3>{{ primaryProject.name }}</h3>
              <p>{{ primaryProject.description }}</p>
              <div class="project-tags">
                <span v-for="tech in primaryProject.techStack.slice(0, 6)" :key="tech">{{ tech }}</span>
              </div>
              <div class="project-actions">
                <a :href="projectHref(primaryProject)" target="_blank" class="project-link project-link--primary">查看项目 →</a>
                <RouterLink to="/projects" class="project-link">全部项目</RouterLink>
              </div>
            </div>
          </article>
        </ScrollReveal>

        <div class="project-preview-grid">
          <ScrollReveal v-for="(project, i) in secondaryProjects" :key="project.id" :delay="(i + 1) * 120">
            <article class="project-preview-card">
              <a class="project-preview-card__media" :href="projectHref(project)" target="_blank">
                <img v-if="project.cover" :src="project.cover" :alt="`${project.name} 项目预览`" />
                <span class="project-badge">{{ project.category }}</span>
              </a>
              <div class="project-preview-card__body">
                <h3>{{ project.name }}</h3>
                <p>{{ project.description }}</p>
                <div class="project-tags">
                  <span v-for="tech in project.techStack.slice(0, 4)" :key="tech">{{ tech }}</span>
                </div>
              </div>
            </article>
          </ScrollReveal>
        </div>
      </div>
      <ScrollReveal :delay="450">
        <div class="section-more">
          <RouterLink to="/projects" class="more-link">查看全部项目 →</RouterLink>
        </div>
      </ScrollReveal>
    </div>
  </section>

  <section class="section section--posts">
    <div class="section-inner">
      <ScrollReveal>
        <SectionTitle title="最近在想" subtitle="一些写下来的碎片" />
      </ScrollReveal>
      <div v-if="store.loading" class="loading-tip">加载中…</div>
      <div v-else class="posts-list">
        <ScrollReveal v-for="(post, i) in recentPosts" :key="post.slug" :delay="i * 80">
          <PostCard :post="post" />
        </ScrollReveal>
      </div>
      <ScrollReveal :delay="400">
        <div class="section-more">
          <RouterLink to="/blog" class="more-link">读更多文章 →</RouterLink>
        </div>
      </ScrollReveal>
    </div>
  </section>

  <footer class="footer">
    <div class="footer-inner">
      <p class="footer-text">起风了，想写点什么</p>
      <p class="footer-copy">© 2026 祁 · 用 Vue 3 + 水豚能量驱动</p>
    </div>
  </footer>
</template>

<style scoped>
.hero { position:relative; min-height:100vh; display:flex; align-items:center; overflow:hidden; }
.hero-glow { position:absolute; top:-10%; right:-5%; width:500px; height:500px; background:radial-gradient(circle,rgba(255,209,102,.18) 0%,transparent 70%); pointer-events:none; }
.hero-inner { position:relative; z-index:1; max-width:896px; margin:0 auto; padding:6rem 1.5rem 4rem; display:flex; align-items:center; justify-content:space-between; gap:3rem; width:100%; }
.hero-text { flex:1; animation:slideUp .8s ease .3s both; }
.hero-title { font-family:'Noto Serif SC',serif; font-size:clamp(42px,6vw,64px); font-weight:700; color:var(--qi-ink); line-height:1.2; margin-bottom:1rem; }
.hero-subtitle { font-size:18px; color:var(--qi-ink-muted); margin-bottom:2rem; animation:fadeIn .6s ease 1.8s both; }
.hero-ctas { display:flex; gap:1rem; flex-wrap:wrap; animation:fadeIn .6s ease 2.2s both; }
.cta-btn { display:inline-block; padding:10px 24px; border-radius:999px; font-size:15px; font-weight:500; text-decoration:none; border:1.5px solid var(--qi-border); color:var(--qi-ink-muted); transition:all .2s; }
.cta-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); transform:translateY(-2px); }
.cta-btn--primary { background:var(--qi-primary); border-color:var(--qi-primary); color:white; }
.cta-btn--primary:hover { opacity:.9; color:white; }
.hero-mascot { flex-shrink:0; animation:slideUp .8s ease .3s both,float 3s ease-in-out 2.5s infinite; }
.scroll-hint { position:absolute; bottom:2rem; left:50%; transform:translateX(-50%); font-size:20px; color:var(--qi-ink-light); animation:scrollHint 2s ease-in-out 3s infinite; }
.section { padding:5rem 0; }
.section--posts { background:var(--qi-bg-muted); }
.section-inner { max-width:1080px; margin:0 auto; padding:0 1.5rem; }
.home-projects { display:grid; gap:1.25rem; margin-bottom:2rem; }
.featured-project {
  display:grid;
  grid-template-columns:minmax(380px, 1.1fr) minmax(0, .9fr);
  overflow:hidden;
  border:1px solid var(--qi-border);
  border-radius:18px;
  background:var(--qi-bg-card);
  box-shadow:0 8px 24px var(--qi-shadow);
}
.featured-project__media,
.project-preview-card__media {
  position:relative;
  display:flex;
  align-items:center;
  justify-content:center;
  overflow:hidden;
  background:linear-gradient(135deg, rgba(255,140,90,.12), rgba(168,216,192,.2));
}
.featured-project__media { min-height:310px; padding:1rem; }
.featured-project__media img,
.project-preview-card__media img {
  width:100%;
  height:100%;
  object-fit:contain;
  display:block;
}
.project-badge {
  position:absolute;
  left:1rem;
  bottom:1rem;
  padding:3px 12px;
  border-radius:999px;
  background:rgba(255,248,240,.92);
  border:1px solid var(--qi-border);
  color:var(--qi-ink-muted);
  font-size:12px;
  font-weight:600;
}
.featured-project__body {
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:2rem;
}
.project-kicker {
  margin-bottom:.45rem;
  color:var(--qi-primary);
  font-size:12px;
  font-weight:700;
}
.featured-project h3,
.project-preview-card h3 {
  color:var(--qi-ink);
  font-family:'Noto Serif SC',serif;
  font-size:26px;
  font-weight:600;
  line-height:1.35;
  margin-bottom:.75rem;
}
.featured-project p,
.project-preview-card p {
  color:var(--qi-ink-muted);
  line-height:1.75;
}
.project-tags {
  display:flex;
  flex-wrap:wrap;
  gap:.45rem;
  margin-top:1rem;
}
.project-tags span {
  padding:3px 9px;
  border-radius:999px;
  background:rgba(168,216,192,.25);
  color:#5A9E82;
  font-size:11px;
  font-weight:600;
}
.project-actions { display:flex; gap:.75rem; flex-wrap:wrap; margin-top:1.35rem; }
.project-link {
  display:inline-flex;
  align-items:center;
  justify-content:center;
  padding:7px 16px;
  border-radius:999px;
  border:1.5px solid var(--qi-border);
  color:var(--qi-ink-muted);
  font-size:13px;
  font-weight:600;
  text-decoration:none;
  transition:all .2s;
}
.project-link:hover { border-color:var(--qi-primary); color:var(--qi-primary); }
.project-link--primary { background:var(--qi-primary); border-color:var(--qi-primary); color:white; }
.project-link--primary:hover { color:white; opacity:.9; }
.project-preview-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1.25rem; }
.project-preview-card {
  overflow:hidden;
  border:1px solid var(--qi-border);
  border-radius:16px;
  background:var(--qi-bg-card);
  transition:transform .2s ease, box-shadow .2s ease;
}
.project-preview-card:hover { transform:translateY(-3px); box-shadow:0 8px 24px var(--qi-shadow); }
.project-preview-card__media { height:190px; padding:.75rem; }
.project-preview-card__body { padding:1.25rem; }
.project-preview-card h3 { font-size:20px; }
.project-preview-card p {
  display:-webkit-box;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
  overflow:hidden;
  font-size:14px;
}
.posts-list { margin-bottom:2rem; }
.section-more { text-align:right; }
.more-link { font-size:14px; font-weight:500; color:var(--qi-primary); text-decoration:none; }
.more-link:hover { opacity:.7; }
.loading-tip { color:var(--qi-ink-light); font-size:14px; padding:2rem 0; }
.footer { padding:3rem 0; text-align:center; border-top:1px solid var(--qi-border); }
.footer-inner { max-width:896px; margin:0 auto; padding:0 1.5rem; }
.footer-text { font-family:'Noto Serif SC',serif; font-size:16px; color:var(--qi-ink-muted); margin-bottom:.5rem; }
.footer-copy { font-size:13px; color:var(--qi-ink-light); }
@media(max-width:768px){
  .hero-inner{flex-direction:column-reverse;text-align:center;padding-top:5rem;}
  .hero-ctas{justify-content:center;}
  .featured-project{grid-template-columns:1fr;}
  .featured-project__media{min-height:230px;}
  .featured-project__body{padding:1.35rem;}
  .project-preview-grid{grid-template-columns:1fr;}
}
@media(max-width:900px){
  .featured-project{grid-template-columns:1fr;}
  .project-preview-grid{grid-template-columns:1fr;}
}
</style>
