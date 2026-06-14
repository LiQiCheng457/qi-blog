<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const STORAGE_KEY = 'qi_chat_history'
const API_BASE = import.meta.env.VITE_API_BASE || ''

const messages = ref<Message[]>([])
const input = ref('')
const loading = ref(false)
const messagesEl = ref<HTMLElement>()
const inputEl = ref<HTMLTextAreaElement>()
const panelEl = ref<HTMLElement>()

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
      x: Math.max(0, Math.min(window.innerWidth - pw, startPx + ev.clientX - startMx)),
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

// ── 历史记录 ────────────────────────────────────────────
onMounted(() => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) messages.value = JSON.parse(raw)
  } catch {}
  if (messages.value.length === 0) {
    messages.value = [{
      role: 'assistant',
      content: '哦，你来了。(￣▽￣)\n有什么想聊的，或者想看看这个博客有什么？',
    }]
  }
  // open 已为 true 时（如 HMR 重载）立即初始化位置
  if (props.open) initPos()
})

function saveHistory() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value))
}

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
  }
})

// ── 发送 ───────────────────────────────────────────────
async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: messages.value.slice(0, -1) }),
    })

    if (!resp.ok || !resp.body) throw new Error('请求失败')

    const reader = resp.body.getReader()
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
    saveHistory()
    await scrollBottom()
    inputEl.value?.focus()
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

function clearHistory() {
  messages.value = [{ role: 'assistant', content: '嗯，清掉了。(￣▽￣) 重新聊吧。' }]
  saveHistory()
}

// ── 消息格式化（支持 markdown 子集） ──────────────────
function esc(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function renderText(text: string): string {
  let s = esc(text)
  // 逐行处理列表项
  s = s.split('\n').map(line => {
    const li = line.match(/^[-*]\s+(.*)$/)
    if (li) return `<span class="ci-li">· ${li[1]}</span>`
    return line
  }).join('\n')
  // 行内样式
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
          <img src="/animations/qi_small.webp" alt="水豚祁" class="header-avatar" />
          <div>
            <span class="header-name">水豚祁</span>
            <span class="header-status">
              <span class="status-dot" :class="{ loading }"></span>
              {{ loading ? '思考中…' : '在线' }}
            </span>
          </div>
        </div>
        <div class="header-actions" @mousedown.stop>
          <button class="icon-btn" title="清空记录" @click="clearHistory">🗑</button>
          <button class="icon-btn" title="关闭" @click="emit('close')">✕</button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div ref="messagesEl" class="chat-messages">
        <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
          <img
            v-if="msg.role === 'assistant'"
            src="/animations/qi_small.webp"
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
          placeholder="说点什么… (Enter 发送，Shift+Enter 换行)"
          :disabled="loading"
          @keydown="onKeydown"
        ></textarea>
        <button class="send-btn" :disabled="!input.trim() || loading" @click="send">
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

.chat-header-info {
  display: flex;
  align-items: center;
  gap: .6rem;
}

.header-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  object-fit: cover;
  pointer-events: none;
}

.header-name {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: var(--qi-ink);
  line-height: 1.3;
}

.header-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--qi-ink-muted);
}

.status-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #6bcb77;
  transition: background .3s;
}
.status-dot.loading {
  background: var(--qi-primary);
  animation: pulse .8s infinite;
}

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .4; } }

.header-actions {
  display: flex;
  gap: .4rem;
  cursor: default;
}

.icon-btn {
  width: 28px; height: 28px;
  border: none;
  background: none;
  color: var(--qi-ink-muted);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s, color .15s;
}
.icon-btn:hover { background: var(--qi-bg-muted); color: var(--qi-ink); }

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
.chat-messages::-webkit-scrollbar-thumb {
  background: var(--qi-border);
  border-radius: 4px;
}

.msg-row {
  display: flex;
  gap: .5rem;
  align-items: flex-end;
}
.msg-row.user { flex-direction: row-reverse; }

.msg-avatar {
  width: 28px; height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

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

/* 打字动画 */
.typing-dots {
  display: inline-flex;
  gap: 3px;
  align-items: center;
  height: 16px;
}
.typing-dots span {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--qi-ink-muted);
  animation: bounce .9s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: .15s; }
.typing-dots span:nth-child(3) { animation-delay: .3s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-5px); }
}

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
  overflow: hidden;          /* 不显示滚动条 */
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
.chat-input:disabled { opacity: .5; }

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
.msg-row.user .msg-text :deep(.ci-ic) {
  background: rgba(255, 255, 255, .22);
}

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

.msg-text :deep(.ci-li) {
  display: block;
  padding-left: .2rem;
  line-height: 1.8;
}

/* 开关动画 */
.chat-panel-enter-active { transition: opacity .22s ease, transform .22s ease; }
.chat-panel-leave-active { transition: opacity .18s ease, transform .18s ease; }
.chat-panel-enter-from,
.chat-panel-leave-to { opacity: 0; transform: translateY(12px) scale(.97); }

/* 移动端：固定底部全宽 */
@media (max-width: 480px) {
  .chat-panel {
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    top: auto !important;
    width: 100% !important;
    height: 72vh !important;
    min-width: unset;
    border-radius: 20px 20px 0 0;
    resize: none;
  }
}
</style>
