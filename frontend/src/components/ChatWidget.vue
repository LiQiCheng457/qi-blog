<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { assetUrl } from '@/utils/assets'
import { useUserStore } from '@/stores/user'
import { getToken } from '@/api/client'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const API_BASE  = import.meta.env.VITE_API_BASE || ''
const qiSmall   = assetUrl('/animations/qi_small.webp')
const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)

const DEFAULT_GREETING: Message = {
  role: 'assistant',
  content: '哦，你来了。(￣▽￣)\n有什么想聊的，或者想看看这个博客有什么？',
}

const messages    = ref<Message[]>([])
const input       = ref('')
const loading     = ref(false)
const histLoading = ref(false)
const messagesEl  = ref<HTMLElement>()
const inputEl     = ref<HTMLTextAreaElement>()
const panelEl     = ref<HTMLElement>()

// ── TTS（阿里云 NLS，后端代理返回 mp3） ────────────────
const autoPlay  = ref(false)
const isPlaying = ref(false)
let   currentAudio: HTMLAudioElement | null = null

function toSpeechText(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, '代码块略，')
    .replace(/`[^`]+`/g, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/^[-*]\s+/gm, '')
    .replace(/\n+/g, ' ')
    .trim()
}

function stopSpeech() {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.src = ''
    currentAudio = null
  }
  isPlaying.value = false
}

async function speakText(text: string) {
  stopSpeech()
  const cleaned = toSpeechText(text)
  if (!cleaned) return

  isPlaying.value = true
  try {
    const token = getToken()
    const resp = await fetch(`${API_BASE}/api/chat/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ text: cleaned }),
    })
    if (!resp.ok) throw new Error(`TTS ${resp.status}`)

    const blob  = await resp.blob()
    const url   = URL.createObjectURL(blob)
    const audio = new Audio(url)
    currentAudio = audio

    audio.onended = () => {
      URL.revokeObjectURL(url)
      if (currentAudio === audio) currentAudio = null
      isPlaying.value = false
    }
    audio.onerror = () => {
      URL.revokeObjectURL(url)
      if (currentAudio === audio) currentAudio = null
      isPlaying.value = false
    }
    await audio.play()
  } catch (e) {
    console.error('TTS error:', e)
    isPlaying.value = false
  }
}

function toggleAutoPlay() {
  if (isPlaying.value) { stopSpeech(); return }
  autoPlay.value = !autoPlay.value
}


// ── 位置（左上角坐标） ──────────────────────────────────
const pos = ref({ x: 0, y: 0 })
let initialized = false

function initPos() {
  if (initialized) return
  initialized = true
  const w = window.innerWidth
  const h = window.innerHeight
  pos.value = {
    x: Math.max(0, w - 360),
    y: Math.max(0, h - 560),
  }
}

// ── 拖拽 ───────────────────────────────────────────────
function onDragStart(e: MouseEvent) {
  if (e.button !== 0) return
  const startMx = e.clientX
  const startMy = e.clientY
  const startPx = pos.value.x
  const startPy = pos.value.y

  function onMove(ev: MouseEvent) {
    const pw = panelEl.value?.offsetWidth ?? 340
    const ph = panelEl.value?.offsetHeight ?? 480
    pos.value = {
      x: Math.max(0, Math.min(window.innerWidth - pw,  startPx + ev.clientX - startMx)),
      y: Math.max(0, Math.min(window.innerHeight - ph, startPy + ev.clientY - startMy)),
    }
  }

  function onUp() {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

// ── 历史记录（从 API 加载） ─────────────────────────────
async function loadHistory() {
  histLoading.value = true
  try {
    const resp = await fetch(`${API_BASE}/api/chat/history`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (resp.ok) {
      const data: Message[] = await resp.json()
      messages.value = data.length > 0 ? data : [{ ...DEFAULT_GREETING }]
    } else {
      messages.value = [{ ...DEFAULT_GREETING }]
    }
  } catch {
    messages.value = [{ ...DEFAULT_GREETING }]
  } finally {
    histLoading.value = false
  }
}

onMounted(async () => {
  if (isLoggedIn.value) {
    await loadHistory()
  }
  if (props.open) initPos()
})

// 登录状态变化时重新加载
watch(isLoggedIn, async (loggedIn) => {
  if (loggedIn) {
    await loadHistory()
  } else {
    messages.value = []
  }
})

// ── 滚底 ───────────────────────────────────────────────
async function scrollBottom() {
  await nextTick()
  if (messagesEl.value)
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}

// ── Textarea 自适应高度 ────────────────────────────────
function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 96) + 'px'
}

watch(input, () => nextTick(autoResize))

// ── 打开时初始化位置 + 聚焦 ────────────────────────────
watch(() => props.open, async (val) => {
  if (val) {
    initPos()
    await scrollBottom()
    await nextTick()
    inputEl.value?.focus()
    autoResize()
  } else {
    stopSpeech()
  }
})

// ── 发送 ───────────────────────────────────────────────
async function send() {
  if (!isLoggedIn.value || !input.value.trim() || loading.value) return

  const text = input.value.trim()
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  await nextTick()
  autoResize()
  await scrollBottom()

  messages.value.push({ role: 'assistant', content: '' })
  const idx = messages.value.length - 1

  try {
    const resp = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ message: text }),
    })

    if (!resp.ok || !resp.body) throw new Error('请求失败')

    const reader  = resp.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      messages.value[idx].content += decoder.decode(value, { stream: true })
      await scrollBottom()
    }
  } catch {
    messages.value[idx].content = '(・_・;) 呃，出了点问题，稍后再试试？'
  } finally {
    loading.value = false
    await scrollBottom()
    inputEl.value?.focus()
    // 自动播放开启时朗读 AI 回复
    if (autoPlay.value) {
      const last = messages.value[messages.value.length - 1]
      if (last?.role === 'assistant' && last.content) speakText(last.content)
    }
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

async function clearHistory() {
  if (!isLoggedIn.value) return
  try {
    await fetch(`${API_BASE}/api/chat/history`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` },
    })
  } catch {}
  messages.value = [{ role: 'assistant', content: '嗯，清掉了。(￣▽￣) 重新聊吧。' }]
}

// ── 消息格式化（支持 markdown 子集） ──────────────────
function esc(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function renderText(text: string): string {
  let s = esc(text)
  s = s.split('\n').map(line => {
    const li = line.match(/^[-*]\s+(.*)$/)
    if (li) return `<span class="ci-li">· ${li[1]}</span>`
    return line
  }).join('\n')
  s = s
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`\n]+)`/g, '<code class="ci-ic">$1</code>')
    .replace(/\n/g, '<br>')
  return s
}

function formatMsg(text: string): string {
  const blocks: Array<{ type: 'text' | 'code'; content: string }> = []
  const re = /```(?:\w*)\n?([\s\S]*?)```/g
  let last = 0, m: RegExpExecArray | null
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) blocks.push({ type: 'text', content: text.slice(last, m.index) })
    blocks.push({ type: 'code', content: m[1] })
    last = m.index + m[0].length
  }
  if (last < text.length) blocks.push({ type: 'text', content: text.slice(last) })

  return blocks.map(b =>
    b.type === 'code'
      ? `<pre class="ci-pre"><code>${esc(b.content)}</code></pre>`
      : renderText(b.content)
  ).join('')
}
</script>

<template>
  <Transition name="chat-panel">
    <div
      v-if="open"
      ref="panelEl"
      class="chat-panel"
      :style="{ left: pos.x + 'px', top: pos.y + 'px' }"
    >
      <!-- 头部（拖拽区） -->
      <div class="chat-header" @mousedown="onDragStart">
        <div class="chat-header-info">
          <img :src="qiSmall" alt="水豚祁" class="header-avatar" />
          <div>
            <span class="header-name">水豚祁</span>
            <span class="header-status">
              <span class="status-dot" :class="{ loading }"></span>
              {{ loading ? '思考中…' : isLoggedIn ? '在线' : '未登录' }}
            </span>
          </div>
        </div>
        <div class="header-actions" @mousedown.stop>
          <button
            v-if="isLoggedIn"
            class="icon-btn"
            :class="{ 'tts-active': autoPlay || isPlaying }"
            :title="isPlaying ? '停止朗读' : autoPlay ? '关闭自动朗读' : '开启自动朗读'"
            @click="toggleAutoPlay"
          >
            <span v-if="isPlaying" class="tts-wave">🔊</span>
            <span v-else-if="autoPlay">🔊</span>
            <span v-else>🔇</span>
          </button>
          <button v-if="isLoggedIn" class="icon-btn" title="清空记录" @click="clearHistory">🗑</button>
          <button class="icon-btn" title="关闭" @click="emit('close')">✕</button>
        </div>
      </div>

      <!-- 未登录锁定状态 -->
      <div v-if="!isLoggedIn" class="chat-locked">
        <img :src="qiSmall" alt="水豚祁" class="lock-avatar" />
        <p class="lock-msg">还没认识你呢~<br>登录之后才能和我聊哦 (´・ω・`)</p>
      </div>

      <!-- 历史加载中 -->
      <div v-else-if="histLoading" class="chat-loading">
        <span class="typing-dots"><span></span><span></span><span></span></span>
        <span class="loading-tip">加载历史记录…</span>
      </div>

      <!-- 消息列表 -->
      <div v-else ref="messagesEl" class="chat-messages">
        <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
          <img
            v-if="msg.role === 'assistant'"
            :src="qiSmall"
            alt="水豚祁"
            class="msg-avatar"
          />
          <div class="msg-bubble">
            <span v-if="msg.content" class="msg-text" v-html="formatMsg(msg.content)"></span>
            <span
              v-else-if="loading && i === messages.length - 1"
              class="typing-dots"
            >
              <span></span><span></span><span></span>
            </span>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input-area">
        <textarea
          ref="inputEl"
          v-model="input"
          class="chat-input"
          :placeholder="isLoggedIn ? '说点什么… (Enter 发送，Shift+Enter 换行)' : '登录后才能发送消息'"
          :disabled="loading || !isLoggedIn"
          @keydown="onKeydown"
        ></textarea>
        <button
          class="send-btn"
          :disabled="!input.trim() || loading || !isLoggedIn"
          @click="send"
        >
          {{ loading ? '…' : '发送' }}
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.chat-panel {
  position: fixed;
  width: 340px;
  height: 480px;
  min-width: 280px;
  min-height: 320px;
  max-width: 600px;
  max-height: 80vh;
  resize: both;
  overflow: hidden;
  background: var(--qi-bg-card);
  border: 1.5px solid var(--qi-border);
  border-radius: 18px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, .14);
  display: flex;
  flex-direction: column;
  z-index: 200;
}

/* 头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: .75rem 1rem;
  border-bottom: 1px solid var(--qi-border);
  flex-shrink: 0;
  cursor: grab;
  user-select: none;
}
.chat-header:active { cursor: grabbing; }

.chat-header-info { display: flex; align-items: center; gap: .6rem; }

.header-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  object-fit: cover;
  pointer-events: none;
}

.header-name { display: block; font-size: 14px; font-weight: 700; color: var(--qi-ink); line-height: 1.3; }

.header-status { display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--qi-ink-muted); }

.status-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #6bcb77;
  transition: background .3s;
}
.status-dot.loading { background: var(--qi-primary); animation: pulse .8s infinite; }

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .4; } }

.header-actions { display: flex; gap: .4rem; cursor: default; }

.icon-btn {
  width: 28px; height: 28px;
  border: none; background: none;
  color: var(--qi-ink-muted);
  border-radius: 8px;
  cursor: pointer; font-size: 13px;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s, color .15s;
}
.icon-btn:hover { background: var(--qi-bg-muted); color: var(--qi-ink); }

/* 未登录锁定 */
.chat-locked {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem 1.5rem;
}
.lock-avatar {
  width: 64px; height: 64px;
  border-radius: 50%;
  object-fit: cover;
  opacity: .65;
  filter: grayscale(.3);
}
.lock-msg {
  font-size: 14px;
  color: var(--qi-ink-muted);
  line-height: 1.8;
  text-align: center;
  margin: 0;
}

/* 历史加载 */
.chat-loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: .75rem;
}
.loading-tip { font-size: 12px; color: var(--qi-ink-light); }

/* 消息区 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: .75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: .75rem;
  min-height: 0;
}

.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-thumb { background: var(--qi-border); border-radius: 4px; }

.msg-row { display: flex; gap: .5rem; align-items: flex-end; }
.msg-row.user { flex-direction: row-reverse; }

.msg-avatar { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }

.msg-bubble {
  max-width: 75%;
  padding: .55rem .8rem;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.65;
  word-break: break-word;
}

.msg-row.assistant .msg-bubble {
  background: var(--qi-bg-muted);
  color: var(--qi-ink);
  border-bottom-left-radius: 4px;
}

.msg-row.user .msg-bubble {
  background: var(--qi-primary);
  color: white;
  border-bottom-right-radius: 4px;
}

/* TTS 开关激活态 */
.icon-btn.tts-active { color: var(--qi-primary); }
.tts-wave { display: inline-block; animation: tts-pulse .6s ease-in-out infinite alternate; }
@keyframes tts-pulse { from { opacity: .5; } to { opacity: 1; } }

/* 打字动画 */
.typing-dots { display: inline-flex; gap: 3px; align-items: center; height: 16px; }
.typing-dots span {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--qi-ink-muted);
  animation: bounce .9s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: .15s; }
.typing-dots span:nth-child(3) { animation-delay: .3s; }

@keyframes bounce { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-5px); } }

/* 输入区 */
.chat-input-area {
  display: flex;
  align-items: flex-end;
  gap: .5rem;
  padding: .65rem 1rem;
  border-top: 1px solid var(--qi-border);
  flex-shrink: 0;
}

.chat-input {
  flex: 1;
  resize: none;
  overflow: hidden;
  border: 1.5px solid var(--qi-border);
  border-radius: 10px;
  padding: .5rem .75rem;
  font-size: 13px;
  font-family: inherit;
  color: var(--qi-ink);
  background: var(--qi-bg);
  transition: border-color .2s;
  line-height: 1.5;
  min-height: 36px;
  max-height: 96px;
}
.chat-input:focus { outline: none; border-color: var(--qi-primary); }
.chat-input:disabled { opacity: .5; cursor: not-allowed; }

.send-btn {
  padding: .45rem .9rem;
  border-radius: 10px;
  border: none;
  background: var(--qi-primary);
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .2s, transform .15s;
  flex-shrink: 0;
  white-space: nowrap;
  height: 36px;
}
.send-btn:hover:not(:disabled) { opacity: .88; transform: translateY(-1px); }
.send-btn:disabled { opacity: .4; cursor: default; }

/* Markdown 渲染元素 */
.msg-text :deep(strong) { font-weight: 600; }

.msg-text :deep(.ci-ic) {
  font-family: 'Fira Code', Consolas, monospace;
  background: rgba(128, 128, 128, .12);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: .88em;
}
.msg-row.user .msg-text :deep(.ci-ic) { background: rgba(255, 255, 255, .22); }

.msg-text :deep(.ci-pre) {
  background: var(--qi-bg-muted);
  border: 1px solid var(--qi-border);
  border-radius: 8px;
  padding: .5rem .75rem;
  margin: .35rem 0;
  overflow-x: auto;
  font-size: .82em;
  font-family: 'Fira Code', Consolas, monospace;
  white-space: pre;
  line-height: 1.55;
}
.msg-row.user .msg-text :deep(.ci-pre) {
  background: rgba(255, 255, 255, .12);
  border-color: rgba(255, 255, 255, .2);
}

.msg-text :deep(.ci-li) { display: block; padding-left: .2rem; line-height: 1.8; }

/* 开关动画 */
.chat-panel-enter-active { transition: opacity .22s ease, transform .22s ease; }
.chat-panel-leave-active { transition: opacity .18s ease, transform .18s ease; }
.chat-panel-enter-from,
.chat-panel-leave-to { opacity: 0; transform: translateY(12px) scale(.97); }

/* 移动端：固定底部全宽 */
@media (max-width: 480px) {
  .chat-panel {
    left: 0 !important; right: 0 !important;
    bottom: 0 !important; top: auto !important;
    width: 100% !important; height: 72vh !important;
    min-width: unset;
    border-radius: 20px 20px 0 0;
    resize: none;
  }
}
</style>
