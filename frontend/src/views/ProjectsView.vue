<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useBlogStore } from '@/stores/blog'
import QiMascot from '@/components/QiMascot.vue'
import ScrollReveal from '@/components/ScrollReveal.vue'
import ProjectCard from '@/components/ProjectCard.vue'

const store = useBlogStore()
const route = useRoute()
const activeCategory = ref('全部')
const categories = ['全部', '前端', '后端', '全栈', 'QT应用', '工具', '设计']

const nameToAnchor = (name: string) => name.replace(/[\s/]+/g, '-')

onMounted(async () => {
  await store.fetchProjects()
  if (route.hash) {
    await nextTick()
    setTimeout(() => {
      const id = decodeURIComponent(route.hash.slice(1))
      const el = document.getElementById(id)
      if (el) {
        const top = el.getBoundingClientRect().top + window.scrollY - 96
        window.scrollTo({ top, behavior: 'smooth' })
      }
    }, 150)
  }
})

const filteredProjects = computed(() => store.getProjectsByCategory(activeCategory.value))

function getProjectRowStyle(index: number) {
  const pattern = ['side-left', 'side-right', 'stack']
  return pattern[index % pattern.length]
}
</script>

<template>
  <div class="projects-page">
    <div class="projects-inner">
      <div class="projects-header">
        <div class="header-text">
          <ScrollReveal>
            <h1 class="page-title">作品集</h1>
            <p class="page-subtitle">一些折腾过的东西，大的小的，完成的和进行中的。</p>
          </ScrollReveal>
          <ScrollReveal :delay="150">
            <div class="filter-tabs">
              <button v-for="cat in categories" :key="cat" class="filter-tab"
                :class="{ active: activeCategory === cat }" @click="activeCategory = cat">
                {{ cat }}
              </button>
            </div>
          </ScrollReveal>
        </div>
        <div class="header-mascot">
          <QiMascot state="type" size="medium" />
        </div>
      </div>

      <div v-if="store.loading" class="empty-state">加载中…</div>
      <div v-else class="projects-list">
        <ScrollReveal
          v-for="(project, i) in filteredProjects"
          :key="project.id"
          :id="nameToAnchor(project.name)"
          class="project-row"
          :class="`project-row--${getProjectRowStyle(i)}`"
          :delay="i * 80"
        >
          <ProjectCard
            :project="project"
            :variant="getProjectRowStyle(i)"
          />
        </ScrollReveal>
        <div v-if="filteredProjects.length === 0" class="empty-state">这个分类暂时还没有项目，水豚也在努力折腾中……</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.projects-page { min-height:100vh; padding-top:80px; background:var(--qi-bg); }
.projects-inner { max-width:1280px; margin:0 auto; padding:4rem 1.5rem; }
.projects-header { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:3rem; gap:2rem; }
.header-text { flex:1; }
.page-title { font-family:'Noto Serif SC',serif; font-size:40px; font-weight:500; color:var(--qi-ink); margin-bottom:.75rem; }
.page-subtitle { font-size:15px; color:var(--qi-ink-muted); margin-bottom:2rem; }
.filter-tabs { display:flex; flex-wrap:wrap; gap:.5rem; }
.filter-tab { font-size:13px; font-weight:500; padding:6px 16px; border-radius:999px; border:1.5px solid var(--qi-border); background:transparent; color:var(--qi-ink-muted); cursor:pointer; transition:all .2s; }
.filter-tab:hover,.filter-tab.active { background:var(--qi-primary); border-color:var(--qi-primary); color:white; }
.projects-list {
  display:flex;
  flex-direction:column;
  gap:1.5rem;
  max-width:1180px;
  margin:0 auto;
}
.project-row {
  width:100%;
}
.empty-state { text-align:center; padding:4rem 0; color:var(--qi-ink-muted); font-size:15px; }
@media(max-width:900px){
  .projects-list { max-width:720px; }
}
@media(max-width:768px){
  .projects-header{flex-direction:column;align-items:center;text-align:center;}
  .filter-tabs{justify-content:center;}
}
</style>
