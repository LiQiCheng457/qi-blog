<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'

const emit = defineEmits<{ close: [] }>()
const user = useUserStore()

const tab      = ref<'login' | 'register'>('login')
const login    = ref('')
const email    = ref('')
const password = ref('')
const username = ref('')
const error    = ref('')
const loading  = ref(false)
const pwdFocus = ref(false)   // 密码框是否聚焦（捂眼模式）

// ── 眼睛跟随鼠标 ───────────────────────────────────────────────
const modalRef = ref<HTMLElement | null>(null)

// 每个角色的眼球偏移量
const eyes = reactive({
  left:  { dx: 0, dy: 0 },
  mid:   { dx: 0, dy: 0 },
  right: { dx: 0, dy: 0 },
})

// 角色眼睛中心点（相对于整个 modal 的大致位置，运行时更精确计算也可以）
const characters = [
  { key: 'left',  cx: 108, cy: 168 },
  { key: 'mid',   cx: 215, cy: 130 },
  { key: 'right', cx: 310, cy: 175 },
] as const

const MAX_MOVE = 5

function onMouseMove(e: MouseEvent) {
  if (!modalRef.value) return
  const rect = modalRef.value.getBoundingClientRect()
  const mx = e.clientX - rect.left
  const my = e.clientY - rect.top

  for (const ch of characters) {
    const dx = mx - ch.cx
    const dy = my - ch.cy
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const scale = Math.min(dist / 120, 1)
    eyes[ch.key].dx = (dx / dist) * MAX_MOVE * scale
    eyes[ch.key].dy = (dy / dist) * MAX_MOVE * scale
  }
}

onMounted(() => window.addEventListener('mousemove', onMouseMove))
onUnmounted(() => window.removeEventListener('mousemove', onMouseMove))

// ── 表单提交 ────────────────────────────────────────────────────
async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (tab.value === 'login') {
      await user.login(login.value.trim(), password.value)
    } else {
      if (!username.value.trim()) { error.value = '请填写用户名'; loading.value = false; return }
      await user.register(username.value.trim(), email.value.trim(), password.value)
    }
    emit('close')
  } catch (e: any) {
    error.value = e.message ?? '操作失败'
  } finally {
    loading.value = false
  }
}

function switchTab(t: 'login' | 'register') {
  tab.value = t
  error.value = ''
}
</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="modal" ref="modalRef">

      <!-- ── 左侧插画区 ─────────────────────────────────── -->
      <div class="panel-left">
        <div class="brand">
          <span class="brand-dot"></span>
          <span class="brand-name">起风了</span>
        </div>

        <!-- SVG 角色区 -->
        <div class="characters">
          <svg viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" class="chars-svg">

            <!-- 角色一：圆润方块（左，暖橙色） -->
            <g class="char char-left">
              <!-- 身体 -->
              <rect x="60" y="110" width="100" height="120" rx="18" fill="#e8956d"/>
              <!-- 耳朵 -->
              <rect x="73" y="100" width="18" height="22" rx="6" fill="#e8956d"/>
              <rect x="109" y="100" width="18" height="22" rx="6" fill="#e8956d"/>

              <!-- 正常状态的眼睛 -->
              <g v-if="!pwdFocus">
                <!-- 眼白左 -->
                <ellipse cx="86" cy="155" rx="11" ry="11" fill="white"/>
                <!-- 瞳孔左 -->
                <circle
                  :cx="86 + eyes.left.dx"
                  :cy="155 + eyes.left.dy"
                  r="5.5" fill="#3a2a1a"/>
                <!-- 高光左 -->
                <circle :cx="86 + eyes.left.dx + 2" :cy="155 + eyes.left.dy - 2" r="2" fill="white"/>

                <!-- 眼白右 -->
                <ellipse cx="114" cy="155" rx="11" ry="11" fill="white"/>
                <!-- 瞳孔右 -->
                <circle
                  :cx="114 + eyes.left.dx"
                  :cy="155 + eyes.left.dy"
                  r="5.5" fill="#3a2a1a"/>
                <!-- 高光右 -->
                <circle :cx="114 + eyes.left.dx + 2" :cy="155 + eyes.left.dy - 2" r="2" fill="white"/>
              </g>

              <!-- 捂眼状态（密码输入时） -->
              <g v-else>
                <rect x="72" y="147" width="56" height="16" rx="8" fill="#c0724a"/>
                <!-- 手指缝 -->
                <line x1="86" y1="147" x2="86" y2="163" stroke="#c0724a" stroke-width="2.5"/>
                <line x1="100" y1="147" x2="100" y2="163" stroke="#c0724a" stroke-width="2.5"/>
                <line x1="114" y1="147" x2="114" y2="163" stroke="#c0724a" stroke-width="2.5"/>
              </g>

              <!-- 嘴巴 -->
              <path v-if="!pwdFocus" d="M92 175 Q100 181 108 175" stroke="#3a2a1a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
              <path v-else           d="M92 178 Q100 174 108 178" stroke="#3a2a1a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            </g>

            <!-- 角色二：高个子（中，深炭灰） -->
            <g class="char char-mid">
              <rect x="170" y="60" width="90" height="160" rx="16" fill="#3a3a3a"/>
              <!-- 耳朵 -->
              <rect x="182" y="50" width="15" height="20" rx="5" fill="#3a3a3a"/>
              <rect x="213" y="50" width="15" height="20" rx="5" fill="#3a3a3a"/>

              <g v-if="!pwdFocus">
                <ellipse cx="199" cy="125" rx="10" ry="10" fill="white"/>
                <circle :cx="199 + eyes.mid.dx" :cy="125 + eyes.mid.dy" r="5" fill="#111"/>
                <circle :cx="199 + eyes.mid.dx + 2" :cy="125 + eyes.mid.dy - 2" r="1.8" fill="white"/>

                <ellipse cx="225" cy="125" rx="10" ry="10" fill="white"/>
                <circle :cx="225 + eyes.mid.dx" :cy="125 + eyes.mid.dy" r="5" fill="#111"/>
                <circle :cx="225 + eyes.mid.dx + 2" :cy="125 + eyes.mid.dy - 2" r="1.8" fill="white"/>
              </g>
              <g v-else>
                <rect x="186" y="118" width="52" height="14" rx="7" fill="#222"/>
                <line x1="199" y1="118" x2="199" y2="132" stroke="#222" stroke-width="2.5"/>
                <line x1="212" y1="118" x2="212" y2="132" stroke="#222" stroke-width="2.5"/>
                <line x1="225" y1="118" x2="225" y2="132" stroke="#222" stroke-width="2.5"/>
              </g>

              <!-- 嘴（横线，面无表情） -->
              <line x1="200" y1="148" x2="222" y2="148" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            </g>

            <!-- 角色三：矮胖（右，薄荷绿） -->
            <g class="char char-right">
              <rect x="270" y="130" width="88" height="100" rx="20" fill="#a8d8c0"/>
              <!-- 耳朵 -->
              <rect x="283" y="120" width="16" height="20" rx="6" fill="#a8d8c0"/>
              <rect x="319" y="120" width="16" height="20" rx="6" fill="#a8d8c0"/>

              <g v-if="!pwdFocus">
                <ellipse cx="299" cy="168" rx="10" ry="10" fill="white"/>
                <circle :cx="299 + eyes.right.dx" :cy="168 + eyes.right.dy" r="5" fill="#2a4a3a"/>
                <circle :cx="299 + eyes.right.dx + 2" :cy="168 + eyes.right.dy - 2" r="1.8" fill="white"/>

                <ellipse cx="325" cy="168" rx="10" ry="10" fill="white"/>
                <circle :cx="325 + eyes.right.dx" :cy="168 + eyes.right.dy" r="5" fill="#2a4a3a"/>
                <circle :cx="325 + eyes.right.dx + 2" :cy="168 + eyes.right.dy - 2" r="1.8" fill="white"/>
              </g>
              <g v-else>
                <rect x="286" y="161" width="52" height="14" rx="7" fill="#7ab89a"/>
                <line x1="299" y1="161" x2="299" y2="175" stroke="#7ab89a" stroke-width="2.5"/>
                <line x1="312" y1="161" x2="312" y2="175" stroke="#7ab89a" stroke-width="2.5"/>
                <line x1="325" y1="161" x2="325" y2="175" stroke="#7ab89a" stroke-width="2.5"/>
              </g>

              <path v-if="!pwdFocus" d="M304 187 Q312 193 320 187" stroke="#2a4a3a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
              <path v-else           d="M304 191 Q312 187 320 191" stroke="#2a4a3a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            </g>

            <!-- 地面阴影 -->
            <ellipse cx="100" cy="235" rx="55" ry="8" fill="rgba(0,0,0,.12)"/>
            <ellipse cx="215" cy="225" rx="50" ry="7" fill="rgba(0,0,0,.12)"/>
            <ellipse cx="314" cy="232" rx="50" ry="7" fill="rgba(0,0,0,.12)"/>
          </svg>
        </div>

        <!-- 底部版权 -->
        <div class="left-footer">
          <span>隐私政策</span>
          <span>服务条款</span>
        </div>
      </div>

      <!-- ── 右侧表单区 ─────────────────────────────────── -->
      <div class="panel-right">
        <button class="close-btn" @click="emit('close')">×</button>

        <h2 class="form-title">{{ tab === 'login' ? '欢迎回来！' : '加入起风了' }}</h2>
        <p class="form-sub">{{ tab === 'login' ? '请输入您的信息' : '创建一个账号' }}</p>

        <!-- Tab 切换 -->
        <div class="tab-row">
          <button :class="['tab', { active: tab === 'login' }]"    @click="switchTab('login')">登录</button>
          <button :class="['tab', { active: tab === 'register' }]" @click="switchTab('register')">注册</button>
        </div>

        <form @submit.prevent="submit" class="form">
          <!-- 注册专属字段 -->
          <template v-if="tab === 'register'">
            <div class="field">
              <label>用户名</label>
              <input v-model="username" type="text" placeholder="2–20 个字符" autocomplete="username" required />
            </div>
            <div class="field">
              <label>电子邮件</label>
              <input v-model="email" type="email" placeholder="you@example.com" autocomplete="email" required />
            </div>
          </template>

          <!-- 登录专属字段 -->
          <template v-else>
            <div class="field">
              <label>账号</label>
              <input v-model="login" type="text" placeholder="用户名 或 邮箱" autocomplete="username" required />
            </div>
          </template>

          <!-- 密码（触发捂眼） -->
          <div class="field">
            <label>密码</label>
            <input
              v-model="password"
              type="password"
              :placeholder="tab === 'register' ? '至少 6 位' : ''"
              autocomplete="current-password"
              required
              @focus="pwdFocus = true"
              @blur="pwdFocus = false"
            />
          </div>

          <p v-if="error" class="error-msg">{{ error }}</p>

          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '处理中…' : tab === 'login' ? '登录' : '注册' }}
          </button>
        </form>

        <p class="switch-tip">
          {{ tab === 'login' ? '没有账号？' : '已有账号？' }}
          <button class="switch-link" @click="switchTab(tab === 'login' ? 'register' : 'login')">
            {{ tab === 'login' ? '注册' : '去登录' }}
          </button>
        </p>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ── 遮罩 ── */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
  backdrop-filter: blur(6px);
}

/* ── 主卡片 ── */
.modal {
  display: flex;
  width: min(860px, 96vw);
  height: min(560px, 94vh);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 24px 64px rgba(0, 0, 0, .3);
  animation: pop .25s cubic-bezier(.34, 1.56, .64, 1);
}
@keyframes pop {
  from { transform: scale(.88); opacity: 0; }
  to   { transform: scale(1);   opacity: 1; }
}

/* ── 左侧 ── */
.panel-left {
  width: 46%;
  flex-shrink: 0;
  background: #4a4e69;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}
.panel-left::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 30% 30%, rgba(168,216,192,.15) 0%, transparent 70%);
  pointer-events: none;
}
.brand {
  display: flex;
  align-items: center;
  gap: .5rem;
  position: relative;
  z-index: 1;
}
.brand-dot {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--qi-primary, #e8906d);
}
.brand-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 600;
  color: rgba(255,255,255,.9);
}
.characters {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: relative;
  z-index: 1;
}
.chars-svg {
  width: 100%;
  max-height: 260px;
}

/* 角色轻微浮动动画 */
.char-left  { animation: float 3.2s ease-in-out infinite; }
.char-mid   { animation: float 2.8s ease-in-out infinite .4s; }
.char-right { animation: float 3.6s ease-in-out infinite .8s; }
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-7px); }
}

.left-footer {
  display: flex;
  gap: 1.5rem;
  position: relative;
  z-index: 1;
}
.left-footer span {
  font-size: 11px;
  color: rgba(255,255,255,.45);
  cursor: default;
}
.left-footer span:hover {
  color: rgba(255,255,255,.7);
}

/* ── 右侧 ── */
.panel-right {
  flex: 1;
  background: var(--qi-bg-card, #fff);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1.75rem 2.5rem;
  position: relative;
  overflow: hidden;
}
.close-btn {
  position: absolute;
  top: 1rem; right: 1.25rem;
  font-size: 22px;
  line-height: 1;
  background: none;
  border: none;
  color: var(--qi-ink-light, #aaa);
  cursor: pointer;
  transition: color .2s;
}
.close-btn:hover { color: var(--qi-ink, #333); }

.form-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 24px; font-weight: 600;
  color: var(--qi-ink, #1a1a1a);
  margin-bottom: .25rem;
}
.form-sub {
  font-size: 13px;
  color: var(--qi-ink-light, #999);
  margin-bottom: 1rem;
}

/* Tab */
.tab-row {
  display: flex;
  border: 1.5px solid var(--qi-border, #e8e0d8);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
}
.tab {
  flex: 1;
  padding: 8px;
  font-size: 14px; font-weight: 500;
  background: transparent;
  border: none;
  color: var(--qi-ink-muted, #888);
  cursor: pointer;
  transition: all .15s;
}
.tab.active { background: var(--qi-primary, #e8906d); color: white; }

/* 表单 */
.form { display: flex; flex-direction: column; gap: .75rem; }
.field { display: flex; flex-direction: column; gap: .3rem; }
.field label {
  font-size: 13px; font-weight: 500;
  color: var(--qi-ink-muted, #888);
}
.field input {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1.5px solid var(--qi-border, #e8e0d8);
  background: var(--qi-bg, #fdf8f4);
  font-size: 14px;
  color: var(--qi-ink, #1a1a1a);
  outline: none;
  transition: border-color .2s;
}
.field input:focus { border-color: var(--qi-primary, #e8906d); }

.error-msg {
  font-size: 13px; color: #e05050;
  background: rgba(224,80,80,.06);
  border: 1px solid rgba(224,80,80,.2);
  border-radius: 8px;
  padding: .6rem .875rem;
  margin: 0;
}

.submit-btn {
  padding: 11px;
  border-radius: 10px;
  background: var(--qi-ink, #1a1a1a);
  color: white;
  font-size: 15px; font-weight: 500;
  border: none; cursor: pointer;
  transition: opacity .2s;
  margin-top: .25rem;
}
.submit-btn:hover:not(:disabled) { opacity: .82; }
.submit-btn:disabled { opacity: .6; cursor: not-allowed; }

.switch-tip {
  font-size: 13px;
  color: var(--qi-ink-light, #999);
  text-align: center;
  margin-top: .75rem;
}
.switch-link {
  font-size: 13px; font-weight: 600;
  color: var(--qi-primary, #e8906d);
  background: none; border: none;
  cursor: pointer; padding: 0;
}

/* ── 响应式：窄屏隐藏左侧 ── */
@media (max-width: 600px) {
  .modal { height: auto; min-height: 70vh; }
  .panel-left { display: none; }
  .panel-right { padding: 2rem 1.5rem; }
}
</style>
