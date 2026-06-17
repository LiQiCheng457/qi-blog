<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { wishesApi, type Wish } from '@/api/wishes'
import { assetUrl } from '@/utils/assets'

const wellBgUrl = assetUrl('/tools/wishing-well-bg.png')
const user = useUserStore()

const stats     = ref<{ total: number }>({ total: 0 })
const input     = ref('')
const throwing  = ref(false)
const rippling  = ref(false)
const revealed  = ref<Wish | null>(null)
const typeText  = ref('')
const showLogin = ref(false)
const showEgg   = ref(false)
const eggCoin   = ref(false)
const throwCount = ref(0)
const errorMsg  = ref('')

const MAX_LEN = 60

// ── 初始化：拉统计 + 围观一条 ───────────────────────────────────────
onMounted(async () => {
  await refreshStats()
  await peek()
})

async function refreshStats() {
  try { stats.value = await wishesApi.stats() }
  catch {}
}

async function peek() {
  try {
    const wish = await wishesApi.random()
    revealed.value = wish
    typeWrite(wish.content)
  } catch {}
}

// ── 打字机效果 ────────────────────────────────────────────────────
let typeTimer: ReturnType<typeof setTimeout> | null = null
function typeWrite(text: string) {
  if (typeTimer) clearTimeout(typeTimer)
  typeText.value = ''
  let i = 0
  function step() {
    if (i <= text.length) {
      typeText.value = text.slice(0, i)
      i++
      typeTimer = setTimeout(step, 45)
    }
  }
  step()
}

// ── 彩蛋：连扔3次 ───────────────────────────────────────────────────
function triggerEgg() {
  showEgg.value = true
  eggCoin.value = false
  setTimeout(() => { eggCoin.value = true }, 100)
  setTimeout(() => {
    showEgg.value = false
    eggCoin.value = false
    throwCount.value = 0
  }, 2800)
}

// ── 投入愿望 ────────────────────────────────────────────────────────
async function throwWish() {
  const text = input.value.trim()
  if (!text || throwing.value) return
  if (!user.isLoggedIn) {
    showLogin.value = true
    return
  }

  // 本地彩蛋（仅用于趣味，不向服务器提交）
  throwCount.value++
  if (throwCount.value >= 3) {
    triggerEgg()
    input.value = ''
    return
  }

  errorMsg.value = ''
  throwing.value = true

  try {
    const myWish = await wishesApi.create(text)
    input.value = ''

    // 硬币落水动画
    await delay(700)
    throwing.value = false
    rippling.value = true
    await delay(400)

    // 捞出别人的（排除自己刚扔的）
    const picked = await wishesApi.random(myWish.id)
    revealed.value = picked
    rippling.value = false
    typeWrite(picked.content)
    await refreshStats()
  } catch (e: any) {
    throwing.value = false
    rippling.value = false
    errorMsg.value = e?.message ?? '投递失败'
  }
}

// ── 共鸣 ────────────────────────────────────────────────────────────
const resonating = ref(false)
async function resonate() {
  if (!revealed.value || resonating.value || revealed.value.has_resonated) return
  if (!user.isLoggedIn) {
    showLogin.value = true
    return
  }
  resonating.value = true
  try {
    const updated = await wishesApi.resonate(revealed.value.id)
    revealed.value = updated
  } catch (e: any) {
    errorMsg.value = e?.message ?? '共鸣失败'
  } finally {
    resonating.value = false
  }
}

function delay(ms: number) { return new Promise(r => setTimeout(r, ms)) }
function dismissLogin() { showLogin.value = false }
</script>

<template>
  <div class="well-widget">
    <!-- 井口背景 -->
    <div class="well-scene">
      <img :src="wellBgUrl" class="well-bg" alt="" />

      <!-- 水波纹 -->
      <div class="ripple-wrap" :class="{ active: rippling }">
        <div class="ripple r1" />
        <div class="ripple r2" />
        <div class="ripple r3" />
      </div>

      <!-- 硬币落水 -->
      <Transition name="coin">
        <div v-if="throwing" class="coin">🪙</div>
      </Transition>

      <!-- 退币彩蛋 -->
      <Transition name="egg">
        <div v-if="showEgg" class="egg-box">
          <div class="egg-coin" :class="{ fly: eggCoin }">🪙</div>
          <p class="egg-text">许愿池觉得你太贪心了</p>
          <p class="egg-sub">悄悄退了一枚硬币给你</p>
        </div>
      </Transition>

      <!-- 登录提示遮罩 -->
      <Transition name="egg">
        <div v-if="showLogin" class="egg-box login-mask" @click.self="dismissLogin">
          <div class="login-icon">🔒</div>
          <p class="egg-text">请先登录</p>
          <p class="egg-sub">只有登录用户才能扔愿望或共鸣</p>
          <button class="login-close" @click="dismissLogin">知道了</button>
        </div>
      </Transition>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <textarea
        v-model="input"
        class="wish-input"
        :placeholder="user.isLoggedIn ? '写下你的愿望，扔进许愿池…' : '登录后即可写下愿望…'"
        rows="2"
        :maxlength="MAX_LEN"
        @keydown.enter.prevent="throwWish"
      />
      <div class="input-footer">
        <span class="char-count">{{ input.length }}/{{ MAX_LEN }}</span>
        <span v-if="errorMsg" class="error-msg">{{ errorMsg }}</span>
        <button
          class="throw-btn"
          :disabled="!input.trim() || throwing"
          @click="throwWish"
        >
          {{ throwing ? '投入中…' : '扔进去' }}
        </button>
      </div>
    </div>

    <!-- 捞出的愿望 -->
    <Transition name="scroll-unfold">
      <div v-if="revealed" class="revealed-card">
        <div class="revealed-label">
          有人许愿
          <span v-if="revealed.is_seed" class="seed-badge">水底古愿</span>
        </div>
        <p class="revealed-text">{{ typeText }}<span class="cursor">|</span></p>
        <div class="revealed-footer">
          <button
            class="resonate-btn"
            :class="{ resonated: revealed.has_resonated }"
            :disabled="resonating"
            @click="resonate"
          >
            <template v-if="revealed.has_resonated">
              已共鸣 · {{ revealed.resonance_count }} 人
            </template>
            <template v-else-if="revealed.resonance_count > 0">
              这也是我的愿望（{{ revealed.resonance_count }}）
            </template>
            <template v-else>
              这也是我的愿望
            </template>
          </button>
        </div>
      </div>
    </Transition>

    <!-- 池子统计 -->
    <div class="pool-stats">
      <span>池中共有 <b>{{ stats.total }}</b> 个愿望</span>
      <span class="stats-dot">·</span>
      <span>每月 1 日自动清空</span>
    </div>
  </div>
</template>

<style scoped>
.well-widget {
  width: 100%;
  display: flex;
  flex-direction: column;
}

/* 井口 */
.well-scene {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #0a1a2a;
}
.well-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: .85;
}

/* 水波 */
.ripple-wrap { position: absolute; inset: 0; pointer-events: none; }
.ripple {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%) scale(0);
  border-radius: 50%;
  border: 2px solid rgba(100, 220, 220, 0.5);
  opacity: 0;
}
.ripple-wrap.active .r1 { animation: ripple-out .9s ease-out .0s forwards; }
.ripple-wrap.active .r2 { animation: ripple-out .9s ease-out .2s forwards; }
.ripple-wrap.active .r3 { animation: ripple-out .9s ease-out .4s forwards; }
@keyframes ripple-out {
  0%   { width: 0; height: 0; opacity: .6; transform: translate(-50%, -50%) scale(1); }
  100% { width: 200px; height: 200px; opacity: 0; transform: translate(-50%, -50%) scale(1); }
}

/* 硬币 */
.coin {
  position: absolute;
  top: 20%; left: 50%;
  transform: translateX(-50%);
  font-size: 1.5rem;
  filter: drop-shadow(0 0 6px rgba(255,210,80,.7));
}
.coin-enter-active { animation: coin-fall .7s ease-in forwards; }
.coin-leave-active { opacity: 0; }
@keyframes coin-fall {
  0%   { top: 10%; opacity: 1; transform: translateX(-50%) rotate(0deg) scale(1); }
  80%  { top: 55%; opacity: 1; transform: translateX(-50%) rotate(720deg) scale(.6); }
  100% { top: 60%; opacity: 0; transform: translateX(-50%) rotate(810deg) scale(.3); }
}

/* 彩蛋/登录蒙层 */
.egg-box {
  position: absolute; inset: 0;
  background: rgba(10,26,42,.78);
  backdrop-filter: blur(4px);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: .5rem; text-align: center; padding: 0 1rem;
}
.egg-coin {
  font-size: 2rem;
  transform: translateY(30px); opacity: 0;
  transition: transform .5s cubic-bezier(.34,1.56,.64,1), opacity .3s;
}
.egg-coin.fly { transform: translateY(-10px); opacity: 1; }
.egg-text { font-size: .95rem; font-weight: 600; color: #ffd166; margin: 0; }
.egg-sub  { font-size: .78rem; color: rgba(255,209,102,.75); margin: 0; }

.login-mask { cursor: pointer; }
.login-icon { font-size: 1.5rem; }
.login-close {
  margin-top: .375rem;
  padding: .35rem 1rem; border-radius: 999px;
  border: 1.5px solid rgba(255,209,102,.45);
  background: none; color: #ffd166;
  font-size: .78rem; cursor: pointer;
  transition: background .2s;
}
.login-close:hover { background: rgba(255,209,102,.12); }

.egg-enter-active, .egg-leave-active { transition: opacity .3s; }
.egg-enter-from, .egg-leave-to { opacity: 0; }

/* 输入区 */
.input-area { padding: 1rem 1rem .5rem; }
.wish-input {
  width: 100%;
  padding: .625rem .75rem;
  border-radius: 10px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-muted);
  color: var(--qi-ink);
  font-size: .875rem;
  line-height: 1.55;
  resize: none; outline: none;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color .2s;
}
.wish-input:focus { border-color: var(--qi-primary); }
.wish-input::placeholder { color: var(--qi-ink-light); }
.input-footer {
  display: flex; align-items: center; justify-content: space-between;
  gap: .5rem;
  margin-top: .5rem;
}
.char-count { font-size: .72rem; color: var(--qi-ink-light); flex-shrink: 0; }
.error-msg  {
  font-size: .72rem; color: #d94f4f;
  flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.throw-btn {
  padding: .4rem 1.125rem;
  border-radius: 8px; border: none;
  background: var(--qi-primary); color: #fff;
  font-size: .84rem; font-weight: 500;
  cursor: pointer; transition: opacity .2s;
  flex-shrink: 0;
}
.throw-btn:hover:not(:disabled) { opacity: .85; }
.throw-btn:disabled { opacity: .4; cursor: default; }

/* 捞出的愿望 */
.revealed-card {
  margin: 0 1rem .75rem;
  background: rgba(10, 40, 60, 0.06);
  border: 1.5px solid rgba(80, 180, 200, 0.2);
  border-radius: 12px;
  padding: .875rem 1rem;
}
.revealed-label {
  display: flex; align-items: center; gap: .4rem;
  font-size: .72rem; color: var(--qi-ink-light); margin-bottom: .3rem;
}
.seed-badge {
  font-size: .62rem; padding: 1px 6px;
  border-radius: 999px;
  background: rgba(168, 216, 192, 0.18);
  color: #3a8a6a;
}
.revealed-text {
  font-size: .9rem; color: var(--qi-ink);
  line-height: 1.65; min-height: 1.65em;
  margin-bottom: .75rem;
}
.cursor {
  display: inline-block;
  animation: blink .7s step-end infinite;
  color: var(--qi-primary); font-weight: 300;
}
@keyframes blink { 50% { opacity: 0; } }

.revealed-footer { display: flex; justify-content: flex-end; }
.resonate-btn {
  font-size: .78rem; padding: .35rem .875rem;
  border-radius: 999px;
  border: 1.5px solid rgba(80,180,200,.3);
  background: none; color: var(--qi-ink-muted);
  cursor: pointer; transition: all .2s;
}
.resonate-btn:hover:not(:disabled) { border-color: var(--qi-primary); color: var(--qi-primary); }
.resonate-btn:disabled { opacity: .5; cursor: default; }
.resonate-btn.resonated {
  background: rgba(255,140,90,.1);
  border-color: var(--qi-primary);
  color: var(--qi-primary);
  cursor: default;
}

.scroll-unfold-enter-active { transition: opacity .4s, transform .4s; }
.scroll-unfold-leave-active { transition: opacity .2s; }
.scroll-unfold-enter-from   { opacity: 0; transform: translateY(8px); }
.scroll-unfold-leave-to     { opacity: 0; }

.pool-stats {
  display: flex; align-items: center; gap: .5rem; justify-content: center;
  padding: .5rem 1rem .875rem;
  font-size: .72rem; color: var(--qi-ink-light);
}
.stats-dot { opacity: .5; }
</style>
