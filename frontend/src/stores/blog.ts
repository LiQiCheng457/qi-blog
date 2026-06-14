import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { postsApi } from '@/api/posts'
import { projectsApi } from '@/api/projects'
import type { Post, Project } from '@/types'

export const useBlogStore = defineStore('blog', () => {
  const posts    = ref<Post[]>([])
  const projects = ref<Project[]>([])
  const postsLoading    = ref(false)
  const projectsLoading = ref(false)
  const loading = computed(() => postsLoading.value || projectsLoading.value)

  async function fetchPosts() {
    postsLoading.value = true
    try { posts.value = await postsApi.list() }
    catch { /* 后端未启动时静默失败 */ }
    finally { postsLoading.value = false }
  }

  async function fetchProjects() {
    projectsLoading.value = true
    try { projects.value = await projectsApi.list() }
    catch { projects.value = [] }
    finally { projectsLoading.value = false }
  }

  function getPostBySlug(slug: string) {
    return posts.value.find(p => p.slug === slug)
  }

  function getFeaturedProjects() {
    return projects.value.filter(p => p.featured).slice(0, 3)
  }

  function getProjectsByCategory(category: string) {
    if (category === '全部') return projects.value
    return projects.value.filter(p => p.category === category)
  }

  function getAllTags() {
    const s = new Set<string>()
    posts.value.forEach(p => p.tags.forEach(t => s.add(t)))
    return Array.from(s)
  }

  return {
    posts, projects, loading,
    fetchPosts, fetchProjects,
    getPostBySlug, getFeaturedProjects,
    getProjectsByCategory, getAllTags,
  }
})
