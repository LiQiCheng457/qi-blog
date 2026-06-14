import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/about', name: 'about', component: () => import('@/views/AboutView.vue') },
    { path: '/projects', name: 'projects', component: () => import('@/views/ProjectsView.vue') },
    { path: '/photos', name: 'photos', component: () => import('@/views/PhotosView.vue') },
    { path: '/blog', name: 'blog', component: () => import('@/views/BlogView.vue') },
    { path: '/blog/:slug', name: 'post', component: () => import('@/views/PostView.vue') },

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

router.beforeEach((to) => {
  const user = useUserStore()

  if (to.meta.requiresAdmin) {
    if (!user.isLoggedIn) {
      // 未登录：回首页，弹登录框由页面自行处理
      return { path: '/', query: { authRequired: '1' } }
    }
    if (!user.isAdmin) {
      return { path: '/' }
    }
  }

  if (to.meta.requiresAuth && !user.isLoggedIn) {
    return { path: '/', query: { authRequired: '1' } }
  }
})

export default router
