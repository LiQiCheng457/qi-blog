import { createRouter, createWebHistory } from 'vue-router'
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

export const isPageLoading = ref(false)

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/about', name: 'about', component: () => import('@/views/AboutView.vue') },
    { path: '/projects', name: 'projects', component: () => import('@/views/ProjectsView.vue') },
    { path: '/photos', name: 'photos', component: () => import('@/views/PhotosView.vue') },
    { path: '/blog', name: 'blog', component: () => import('@/views/BlogView.vue') },
    { path: '/blog/:slug', name: 'post', component: () => import('@/views/PostView.vue') },
    { path: '/tools', name: 'tools', component: () => import('@/views/ToolsView.vue') },
    { path: '/games', name: 'games', component: () => import('@/views/GamesView.vue') },
    { path: '/games/2048', name: 'blog2048', component: () => import('@/views/games/Blog2048View.vue') },

    // 个人资料（所有登录用户）
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },

    // /admin/login → 重定向到首页（统一登录用弹窗）
    { path: '/admin/login', redirect: '/' },

    // 后台（需要 admin 角色）
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAdmin: true },
      children: [
        { path: '', name: 'admin-dashboard', component: () => import('@/views/admin/AdminDashboard.vue') },
        { path: 'posts', name: 'admin-posts', component: () => import('@/views/admin/AdminPosts.vue') },
        { path: 'posts/new', name: 'admin-post-new', component: () => import('@/views/admin/AdminPostEdit.vue') },
        { path: 'posts/:slug/edit', name: 'admin-post-edit', component: () => import('@/views/admin/AdminPostEdit.vue') },
        { path: 'projects', name: 'admin-projects', component: () => import('@/views/admin/AdminProjects.vue') },
        { path: 'photos',   name: 'admin-photos',   component: () => import('@/views/admin/AdminPhotos.vue') },
        { path: 'exes',     name: 'admin-exes',     component: () => import('@/views/admin/AdminExes.vue') },
        { path: 'users',    name: 'admin-users',    component: () => import('@/views/admin/AdminUsers.vue') },
        { path: 'comments', name: 'admin-comments', component: () => import('@/views/admin/AdminComments.vue') },
        { path: 'chat',     name: 'admin-chat',     component: () => import('@/views/admin/AdminChat.vue') },
        { path: 'wishes',   name: 'admin-wishes',   component: () => import('@/views/admin/AdminWishes.vue') },
      ],
    },

    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return false // 目标页自行处理锚点滚动
    return { top: 0, behavior: 'smooth' }
  },
})

// ── 页面加载动画守卫（在此注册，避免 HMR 重复累积） ──────
let loadingTimer: ReturnType<typeof setTimeout> | null = null

router.beforeEach((to) => {
  const user = useUserStore()

  if (to.meta.requiresAdmin) {
    if (!user.isLoggedIn) return { path: '/', query: { authRequired: '1' } }
    if (!user.isAdmin)    return { path: '/' }
  }
  if (to.meta.requiresAuth && !user.isLoggedIn) {
    return { path: '/', query: { authRequired: '1' } }
  }

  // 200ms 防抖，快速跳转不显示遮罩
  loadingTimer = setTimeout(() => { isPageLoading.value = true }, 200)
})

router.afterEach(() => {
  if (loadingTimer) { clearTimeout(loadingTimer); loadingTimer = null }
  isPageLoading.value = false
})

export default router
