<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { assetUrl } from '@/utils/assets'
import UserAuthModal from './UserAuthModal.vue'

const scrolled     = ref(false)
const menuOpen     = ref(false)
const showAuth     = ref(false)
const showUserMenu = ref(false)
const router       = useRouter()
const user         = useUserStore()
const theme        = useThemeStore()

function openAuthModal() {
  showUserMenu.value = false
  showAuth.value = true
}

function switchAccount() {
  user.logout()
  showUserMenu.value = false
  showAuth.value = true
}

function logout() {
  user.logout()
  showUserMenu.value = false
}

function onClickOutside(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('.navbar-user')) {
    showUserMenu.value = false
  }
}

const onScroll = () => { scrolled.value = window.scrollY > 80 }

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('click', onClickOutside)
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onClickOutside)
})

const navLinks = [
  { name: '首页', path: '/' },
  { name: '关于', path: '/about' },
  { name: '项目', path: '/projects' },
  { name: '相册', path: '/photos' },
  { name: '文章', path: '/blog' },
  { name: '工具', path: '/tools' },
  { name: '游戏', path: '/games' },
]

function navigate(path: string) {
  menuOpen.value = false
  router.push(path)
}

/** 头像首字母（有 avatar URL 时用图片，否则用字母） */
const initials = () => (user.profile?.username?.[0] ?? '?').toUpperCase()
const qiSmall = assetUrl('/animations/qi_small.webp')
</script>

<template>
  <header class="navbar" :class="{ scrolled, 'navbar--dark': theme.isDark }">
    <div class="navbar-inner">
      <!-- Logo -->
      <RouterLink to="/" class="navbar-logo" @click="menuOpen = false">
        <picture>
          <source :srcset="qiSmall" type="image/webp" />
          <img :src="qiSmall" alt="祁" class="logo-img" />
        </picture>
        <span class="navbar-title">起风了</span>
      </RouterLink>

      <!-- 桌面端导航 -->
      <nav class="navbar-links">
        <RouterLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          class="navbar-link"
          active-class="navbar-link--active"
          exact-active-class="navbar-link--active"
        >
          {{ link.name }}
        </RouterLink>
      </nav>

      <!-- 暗色模式切换 -->
      <button class="theme-toggle" @click="theme.toggle" :title="theme.isDark ? '切换亮色' : '切换暗色'" aria-label="切换主题">
        <span v-if="theme.isDark">☀️</span>
        <span v-else>🌙</span>
      </button>

      <!-- 用户头像区 -->
      <div class="navbar-user">
        <!-- 未登录 -->
        <button v-if="!user.isLoggedIn" class="btn-login" @click="openAuthModal">
          登录 / 注册
        </button>

        <!-- 已登录：头像 chip + 下拉菜单 -->
        <div v-else class="user-chip-wrap">
          <button class="user-chip" @click.stop="showUserMenu = !showUserMenu">
            <!-- 自定义头像 -->
            <img
              v-if="user.profile?.avatar"
              :src="assetUrl(user.profile.avatar)"
              class="chip-avatar"
              :alt="user.profile.username"
            />
            <!-- 首字母头像 -->
            <span v-else class="chip-initials">{{ initials() }}</span>
            <span class="chip-name">{{ user.profile?.username }}</span>
            <span class="chip-arrow" :class="{ open: showUserMenu }">▾</span>
          </button>

          <Transition name="dropdown">
            <div v-if="showUserMenu" class="user-dropdown">
              <div class="dropdown-header">
                <span class="d-role" :class="user.isAdmin ? 'admin' : 'reader'">
                  {{ user.isAdmin ? '博主' : '读者' }}
                </span>
                <span class="d-name">{{ user.profile?.username }}</span>
                <span class="d-email">{{ user.profile?.email }}</span>
              </div>
              <hr class="dropdown-divider" />
              <RouterLink class="dropdown-item" to="/profile" @click="showUserMenu = false">
                个人资料
              </RouterLink>
              <RouterLink v-if="user.isAdmin" class="dropdown-item" to="/admin" @click="showUserMenu = false">
                后台管理
              </RouterLink>
              <hr class="dropdown-divider" />
              <button class="dropdown-item" @click="switchAccount">切换账号</button>
              <button class="dropdown-item danger" @click="logout">退出登录</button>
            </div>
          </Transition>
        </div>
      </div>

      <!-- 登录弹窗 -->
      <Teleport to="body">
        <UserAuthModal v-if="showAuth" @close="showAuth = false" />
      </Teleport>

      <!-- 移动端汉堡 -->
      <button class="navbar-burger" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen" aria-label="菜单">
        <span :class="{ open: menuOpen }"></span>
        <span :class="{ open: menuOpen }"></span>
        <span :class="{ open: menuOpen }"></span>
      </button>
    </div>

    <!-- 移动端全屏菜单 -->
    <Transition name="menu">
      <div v-if="menuOpen" class="navbar-mobile-menu">
        <button class="mobile-close" @click="menuOpen = false">
          <picture>
            <source :srcset="qiSmall" type="image/webp" />
            <img :src="qiSmall" alt="关闭" />
          </picture>
        </button>
        <nav>
          <button v-for="link in navLinks" :key="link.path" class="mobile-link" @click="navigate(link.path)">
            {{ link.name }}
          </button>
          <template v-if="user.isLoggedIn">
            <button class="mobile-link" @click="navigate('/profile')">个人资料</button>
            <button v-if="user.isAdmin" class="mobile-link mobile-link--admin" @click="navigate('/admin')">
              后台管理
            </button>
            <button class="mobile-link mobile-link--logout" @click="logout">退出登录</button>
          </template>
          <template v-else>
            <button class="mobile-link mobile-link--login" @click="() => { menuOpen = false; showAuth = true }">
              登录 / 注册
            </button>
          </template>
        </nav>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: var(--qi-navbar-z);
  width: 100%;
  height: 72px;
  overflow: visible;
  background: var(--navbar-bg);
  border-bottom: 1px solid var(--navbar-border);
  color: var(--navbar-title-color);
  backdrop-filter: blur(12px);
  transition: height .3s ease, background .3s ease, box-shadow .3s ease;
}
.navbar.scrolled {
  height: 56px;
  background: var(--navbar-scrolled-bg);
  box-shadow: var(--navbar-scrolled-shadow);
  border-bottom-color: var(--navbar-border);
}
.navbar-inner {
  max-width: 896px;
  margin: 0 auto;
  height: 100%;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.navbar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}
.logo-img { width: 32px; height: 32px; object-fit: contain; }
.navbar-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px; font-weight: 700;
  color: var(--navbar-title-color);
}
.navbar-links {
  display: flex;
  gap: 2rem;
  flex: 1;
  justify-content: center;
}
.navbar-link {
  font-size: 15px; font-weight: 500;
  color: var(--navbar-link-color);
  text-decoration: none;
  transition: color .2s;
  position: relative;
}
.navbar-link::after {
  content: '';
  position: absolute;
  bottom: -4px; left: 0;
  width: 0; height: 2px;
  background: var(--qi-primary);
  border-radius: 999px;
  transition: width .2s;
}
.navbar-link:hover,
.navbar-link--active { color: var(--qi-primary); }
.navbar-link:hover::after,
.navbar-link--active::after { width: 100%; }
.logo-img { filter: var(--navbar-logo-filter, none); }

/* 暗色切换 */
.theme-toggle {
  flex-shrink: 0;
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 1.5px solid var(--navbar-control-border);
  background: var(--navbar-control-bg);
  color: var(--navbar-control-color);
  cursor: pointer;
  font-size: 15px;
  display: flex; align-items: center; justify-content: center;
  transition: border-color .2s, transform .2s;
}
.theme-toggle:hover { border-color: var(--qi-primary); transform: scale(1.1); }

/* 用户区 */
.navbar-user { flex-shrink: 0; }

.btn-login {
  font-size: 13px; font-weight: 500;
  padding: 5px 14px;
  border-radius: 999px;
  border: 1.5px solid var(--navbar-control-border);
  background: var(--navbar-control-bg);
  color: var(--navbar-control-color);
  cursor: pointer;
  transition: all .2s;
}
.btn-login:hover { border-color: var(--qi-primary); color: var(--qi-primary); }

/* chip */
.user-chip-wrap { position: relative; }
.user-chip {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  padding: 4px 10px 4px 4px;
  border-radius: 999px;
  border: 1.5px solid var(--navbar-control-border);
  background: var(--navbar-control-bg);
  cursor: pointer;
  transition: all .2s;
}
.user-chip:hover { border-color: var(--qi-primary); }

.chip-avatar {
  width: 26px; height: 26px;
  border-radius: 50%;
  object-fit: cover;
}
.chip-initials {
  width: 26px; height: 26px;
  border-radius: 50%;
  background: var(--navbar-avatar-gradient);
  color: var(--navbar-avatar-color);
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.chip-name {
  font-size: 13px; font-weight: 500;
  color: var(--navbar-control-color);
  max-width: 80px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.chip-arrow {
  font-size: 11px;
  color: var(--qi-ink-light);
  transition: transform .2s;
  line-height: 1;
}
.chip-arrow.open { transform: rotate(180deg); }

/* 下拉菜单 */
.user-dropdown {
  position: absolute;
  top: calc(100% + 8px); right: 0;
  width: 192px;
  background: var(--navbar-dropdown-bg);
  border: 1.5px solid var(--qi-border);
  border-radius: 12px;
  box-shadow: var(--navbar-dropdown-shadow);
  overflow: hidden;
  z-index: 200;
}
.dropdown-header { padding: .75rem 1rem .625rem; }
.d-role {
  display: inline-block;
  font-size: 10px; font-weight: 700;
  padding: 1px 6px;
  border-radius: 999px;
  margin-bottom: .3rem;
}
.d-role.admin { background: var(--navbar-admin-bg); color: var(--qi-primary); }
.d-role.reader { background: var(--navbar-reader-bg); color: var(--navbar-reader-color); }
.d-name { display: block; font-size: 13px; font-weight: 600; color: var(--qi-ink); margin-bottom: .15rem; }
.d-email { display: block; font-size: 11px; color: var(--qi-ink-light); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.dropdown-divider { border: none; border-top: 1px solid var(--qi-border); margin: 0; }
.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: .625rem 1rem;
  font-size: 13px; font-weight: 500;
  color: var(--qi-ink-muted);
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: background .15s;
}
.dropdown-item:hover { background: var(--qi-bg-muted); color: var(--qi-ink); }
.dropdown-item.danger { color: var(--navbar-danger-color); }
.dropdown-item.danger:hover { background: var(--navbar-danger-bg); }

.dropdown-enter-active, .dropdown-leave-active { transition: opacity .15s, transform .15s; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px); }

/* 汉堡 */
.navbar-burger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  flex-shrink: 0;
}
.navbar-burger span {
  display: block;
  width: 22px; height: 2px;
  background: var(--navbar-title-color);
  border-radius: 2px;
  transition: all .3s;
}
.navbar-burger span.open:nth-child(1) { transform: rotate(45deg) translate(5px,5px); }
.navbar-burger span.open:nth-child(2) { opacity: 0; }
.navbar-burger span.open:nth-child(3) { transform: rotate(-45deg) translate(5px,-5px); }

/* 移动菜单 */
.navbar-mobile-menu {
  position: fixed; inset: 0;
  background: var(--qi-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  z-index: calc(var(--qi-navbar-z) + 1);
}
.mobile-close {
  position: absolute;
  top: 1.5rem; right: 1.5rem;
  background: none; border: none; cursor: pointer;
}
.mobile-close img { width: 40px; height: 40px; object-fit: contain; }
.mobile-link {
  font-family: 'Noto Serif SC', serif;
  font-size: 28px; font-weight: 500;
  color: var(--qi-ink);
  background: none; border: none;
  cursor: pointer;
  transition: color .2s;
}
.mobile-link:hover { color: var(--qi-primary); }
.mobile-link--admin { font-size: 18px; color: var(--qi-ink-light); margin-top: .5rem; }
.mobile-link--login { font-size: 20px; color: var(--qi-primary); }
.mobile-link--logout { font-size: 16px; color: var(--navbar-danger-color); margin-top: .5rem; }

.menu-enter-active, .menu-leave-active { transition: opacity .25s; }
.menu-enter-from, .menu-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .navbar-links { display: none; }
  .navbar-user { display: none; }
  .navbar-burger { display: flex; }
}
</style>
