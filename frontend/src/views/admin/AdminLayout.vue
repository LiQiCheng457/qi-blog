<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const user   = useUserStore()

function logout() {
  user.logout()
  router.push('/')
}
</script>

<template>
  <div class="admin-wrap">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">🐾</span>
        <span class="brand-name">起风了后台</span>
      </div>
      <nav class="sidebar-nav">
        <RouterLink to="/admin"          class="nav-item" exact-active-class="active">概览</RouterLink>
        <RouterLink to="/admin/posts"    class="nav-item" active-class="active">文章管理</RouterLink>
        <RouterLink to="/admin/projects" class="nav-item" active-class="active">项目管理</RouterLink>
        <RouterLink to="/admin/photos"   class="nav-item" active-class="active">图片管理</RouterLink>
      </nav>
      <div class="sidebar-footer">
        <RouterLink class="nav-item" to="/profile">个人资料</RouterLink>
        <a class="nav-item" href="/" target="_blank">查看博客</a>
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </aside>

    <main class="admin-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.admin-wrap { display:flex; min-height:100vh; background:var(--qi-bg); }
.sidebar { width:220px; flex-shrink:0; background:var(--qi-bg-card); border-right:1px solid var(--qi-border); display:flex; flex-direction:column; padding:1.5rem 0; position:sticky; top:0; height:100vh; }
.sidebar-brand { display:flex; align-items:center; gap:.75rem; padding:0 1.25rem 1.5rem; border-bottom:1px solid var(--qi-border); margin-bottom:1rem; }
.brand-icon { font-size:24px; }
.brand-name { font-size:14px; font-weight:600; color:var(--qi-ink); }
.sidebar-nav { flex:1; display:flex; flex-direction:column; gap:2px; padding:0 .75rem; }
.nav-item { display:block; padding:8px 12px; border-radius:8px; font-size:14px; color:var(--qi-ink-muted); text-decoration:none; cursor:pointer; transition:all .15s; }
.nav-item:hover,.nav-item.active { background:rgba(255,140,90,.1); color:var(--qi-primary); }
.sidebar-footer { padding:.75rem; border-top:1px solid var(--qi-border); display:flex; flex-direction:column; gap:2px; }
.logout-btn { all:unset; display:block; padding:8px 12px; border-radius:8px; font-size:14px; color:var(--qi-ink-light); cursor:pointer; transition:all .15s; }
.logout-btn:hover { background:rgba(224,80,80,.08); color:#e05050; }
.admin-main { flex:1; min-width:0; padding:2rem 2.5rem; width:0; }
@media(max-width:768px){
  .admin-wrap{flex-direction:column;}
  .sidebar{width:100%;height:auto;position:static;flex-direction:row;flex-wrap:wrap;padding:.75rem;}
  .sidebar-nav{flex-direction:row;flex:unset;padding:0;}
  .sidebar-brand{padding-bottom:.75rem;border-bottom:none;margin-bottom:0;}
  .sidebar-footer{flex-direction:row;border-top:none;}
  .admin-main{padding:1.5rem 1rem;}
}
</style>
