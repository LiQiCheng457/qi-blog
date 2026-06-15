<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { ChatUserStat, ChatMsgRecord } from '@/api/admin'
import { assetUrl } from '@/utils/assets'

const qiSmall = assetUrl('/animations/qi_small.webp')

// ── 用户列表视图 ────────────────────────────────────────────────────────────
const users    = ref<ChatUserStat[]>([])
const loading  = ref(true)
const error    = ref('')
const search   = ref('')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(u => u.username.toLowerCase().includes(q))
})

async function loadUsers() {
  loading.value = true
  error.value   = ''
  try { users.value = await adminApi.listChatUsers() }
  catch (e: any) { error.value = e.message ?? '加载失败' }
  finally { loading.value = false }
}

onMounted(loadUsers)

// ── 对话详情视图 ────────────────────────────────────────────────────────────
const activeUser  = ref<ChatUserStat | null>(null)
const messages    = ref<ChatMsgRecord[]>([])
const detailLoading = ref(false)

async function openUser(u: ChatUserStat) {
  activeUser.value  = u
  detailLoading.value = true
  messages.value    = []
  try { messages.value = await adminApi.getUserChat(u.user_id) }
  catch (e: any) { error.value = e.message ?? '加载失败' }
  finally { detailLoading.value = false }
}

function backToList() {
  activeUser.value = null
  messages.value   = []
}

async function clearChat(u: ChatUserStat) {
  if (!confirm(`确定清空「${u.username}」的全部聊天记录？此操作不可恢复。`)) return
  try {
    await adminApi.clearUserChat(u.user_id)
    users.value = users.value.filter(x => x.user_id !== u.user_id)
    if (activeUser.value?.user_id === u.user_id) backToList()
  } catch (e: any) {
    alert(e.message ?? '清空失败')
  }
}

// ── 工具函数 ────────────────────────────────────────────────────────────────
function formatDate(s: string) {
  return new Date(s).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

function formatDateShort(s: string) {
  return new Date(s).toLocaleDateString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
  })
}

// 消息格式化（与 ChatWidget 相同的子集）
function esc(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}
function renderText(text: string): string {
  let s = esc(text)
  s = s.split('\n').map(line => {
    const li = line.match(/^[-*]\s+(.*)$/)
    return li ? `<span class="ci-li">· ${li[1]}</span>` : line
  }).join('\n')
  return s
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`\n]+)`/g, '<code class="ci-ic">$1</code>')
    .replace(/\n/g, '<br>')
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
  <div class="admin-chat">

    <!-- ── 用户列表视图 ── -->
    <template v-if="!activeUser">
      <div class="page-header">
        <div>
          <h1 class="page-title">对话管理</h1>
          <p class="page-sub">共 {{ users.length }} 位用户有聊天记录</p>
        </div>
        <input v-model="search" class="search-input" type="text" placeholder="搜索用户名…" />
      </div>

      <div v-if="error" class="err-msg">{{ error }}</div>
      <div v-else-if="loading" class="empty">加载中…</div>
      <div v-else-if="filtered.length === 0" class="empty">暂无聊天记录</div>
      <div v-else class="user-list">
        <div v-for="u in filtered" :key="u.user_id" class="user-row">
          <div class="user-avatar">
            <img v-if="u.avatar" :src="u.avatar" :alt="u.username" />
            <span v-else class="avatar-fallback">{{ u.username[0] }}</span>
          </div>
          <div class="user-info">
            <div class="user-name-row">
              <span class="user-name">{{ u.username }}</span>
              <span v-if="u.role === 'admin'" class="role-badge role-badge--admin">管理员</span>
              <span v-else class="role-badge">读者</span>
            </div>
            <span class="user-meta">
              共 {{ u.message_count }} 条消息 · 最近活跃 {{ formatDateShort(u.last_at) }}
            </span>
          </div>
          <div class="row-actions">
            <button class="view-btn" @click="openUser(u)">查看对话</button>
            <button class="del-btn" @click="clearChat(u)">清空</button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── 对话详情视图 ── -->
    <template v-else>
      <div class="detail-header">
        <button class="back-btn" @click="backToList">← 返回</button>
        <div class="detail-user">
          <div class="user-avatar sm">
            <img v-if="activeUser.avatar" :src="activeUser.avatar" :alt="activeUser.username" />
            <span v-else class="avatar-fallback">{{ activeUser.username[0] }}</span>
          </div>
          <div>
            <span class="detail-name">{{ activeUser.username }}</span>
            <span class="detail-meta">{{ activeUser.message_count }} 条消息</span>
          </div>
        </div>
        <button class="del-btn" @click="clearChat(activeUser)">清空记录</button>
      </div>

      <div v-if="detailLoading" class="empty">加载中…</div>
      <div v-else-if="messages.length === 0" class="empty">暂无消息</div>
      <div v-else class="chat-view">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="msg-row"
          :class="msg.role"
        >
          <!-- assistant 头像 -->
          <img
            v-if="msg.role === 'assistant'"
            :src="qiSmall"
            alt="水豚祁"
            class="msg-avatar"
          />
          <div class="msg-col">
            <div class="msg-bubble">
              <span class="msg-text" v-html="formatMsg(msg.content)"></span>
            </div>
            <span class="msg-time">{{ formatDate(msg.created_at) }}</span>
          </div>
          <!-- user 头像 -->
          <div v-if="msg.role === 'user'" class="user-avatar sm">
            <img v-if="activeUser.avatar" :src="activeUser.avatar" :alt="activeUser.username" />
            <span v-else class="avatar-fallback">{{ activeUser.username[0] }}</span>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<style scoped>
.admin-chat { width: 100%; }

/* ── 页头 ── */
.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; margin-bottom:2rem; flex-wrap:wrap; }
.page-title { font-family:'Noto Serif SC',serif; font-size:28px; font-weight:500; color:var(--qi-ink); margin-bottom:.25rem; }
.page-sub { font-size:13px; color:var(--qi-ink-muted); }
.search-input {
  padding:8px 14px; border-radius:8px; border:1.5px solid var(--qi-border);
  background:var(--qi-bg); font-size:13.5px; color:var(--qi-ink);
  outline:none; width:200px; font-family:inherit; transition:border-color .15s;
}
.search-input:focus { border-color:var(--qi-primary); }
.err-msg { color:#e05050; font-size:13.5px; }
.empty { color:var(--qi-ink-light); font-size:14px; padding:2rem 0; }

/* ── 用户列表 ── */
.user-list { display:flex; flex-direction:column; gap:.4rem; }
.user-row {
  display:flex; align-items:center; gap:.9rem;
  background:var(--qi-bg-card); border:1px solid var(--qi-border);
  border-radius:12px; padding:.75rem 1rem; transition:border-color .15s;
}
.user-row:hover { border-color:rgba(255,140,90,.3); }

.user-avatar {
  flex-shrink:0; width:40px; height:40px;
  border-radius:50%; overflow:hidden; border:1px solid var(--qi-border);
}
.user-avatar.sm { width:32px; height:32px; }
.user-avatar img { width:100%; height:100%; object-fit:cover; }
.avatar-fallback {
  width:100%; height:100%; display:flex; align-items:center; justify-content:center;
  background:var(--qi-bg-muted); font-size:14px; font-weight:600; color:var(--qi-primary);
}

.user-info { flex:1; min-width:0; }
.user-name-row { display:flex; align-items:center; gap:.5rem; margin-bottom:.15rem; }
.user-name { font-size:14px; font-weight:500; color:var(--qi-ink); }
.user-meta { font-size:12px; color:var(--qi-ink-light); }

.role-badge {
  font-size:10px; font-weight:600; padding:2px 7px; border-radius:999px;
  background:rgba(168,216,192,.25); color:#5A9E82;
}
.role-badge--admin { background:rgba(255,140,90,.12); color:var(--qi-primary); }

.row-actions { display:flex; gap:.5rem; flex-shrink:0; }
.view-btn {
  font-size:12px; padding:5px 14px; border-radius:7px;
  border:1.5px solid var(--qi-border); background:transparent;
  color:var(--qi-ink-muted); cursor:pointer; transition:all .15s;
}
.view-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); }
.del-btn {
  font-size:12px; padding:5px 12px; border-radius:7px;
  border:none; background:transparent; color:#e05050; cursor:pointer; transition:background .15s;
}
.del-btn:hover { background:rgba(224,80,80,.08); }

/* ── 对话详情头部 ── */
.detail-header {
  display:flex; align-items:center; gap:1rem;
  margin-bottom:1.5rem; flex-wrap:wrap;
}
.back-btn {
  all:unset; cursor:pointer; font-size:13.5px; color:var(--qi-ink-muted);
  padding:6px 12px; border-radius:8px; border:1.5px solid var(--qi-border);
  transition:all .15s; flex-shrink:0;
}
.back-btn:hover { color:var(--qi-ink); border-color:var(--qi-ink-muted); }
.detail-user { display:flex; align-items:center; gap:.6rem; flex:1; min-width:0; }
.detail-name { font-size:15px; font-weight:600; color:var(--qi-ink); display:block; }
.detail-meta { font-size:12px; color:var(--qi-ink-light); }

/* ── 对话气泡视图 ── */
.chat-view {
  display:flex; flex-direction:column; gap:.9rem;
  max-height:calc(100vh - 220px); overflow-y:auto;
  padding-right:.25rem;
}
.chat-view::-webkit-scrollbar { width:4px; }
.chat-view::-webkit-scrollbar-thumb { background:var(--qi-border); border-radius:4px; }

.msg-row { display:flex; align-items:flex-end; gap:.6rem; }
.msg-row.user { flex-direction:row-reverse; }

.msg-avatar { width:32px; height:32px; border-radius:50%; object-fit:cover; flex-shrink:0; }

.msg-col { display:flex; flex-direction:column; gap:.25rem; max-width:72%; }
.msg-row.user .msg-col { align-items:flex-end; }

.msg-bubble {
  padding:.55rem .85rem; border-radius:14px;
  font-size:13px; line-height:1.65; word-break:break-word;
}
.msg-row.assistant .msg-bubble {
  background:var(--qi-bg-muted); color:var(--qi-ink);
  border-bottom-left-radius:4px;
}
.msg-row.user .msg-bubble {
  background:var(--qi-primary); color:#fff;
  border-bottom-right-radius:4px;
}

.msg-time { font-size:11px; color:var(--qi-ink-light); padding:0 .1rem; }

/* Markdown 内联渲染 */
.msg-text :deep(strong) { font-weight:600; }
.msg-text :deep(.ci-ic) {
  font-family:'Fira Code',Consolas,monospace;
  background:rgba(128,128,128,.12); padding:1px 5px;
  border-radius:4px; font-size:.88em;
}
.msg-row.user .msg-text :deep(.ci-ic) { background:rgba(255,255,255,.22); }
.msg-text :deep(.ci-pre) {
  background:var(--qi-bg-muted); border:1px solid var(--qi-border);
  border-radius:8px; padding:.5rem .75rem; margin:.35rem 0;
  overflow-x:auto; font-size:.82em;
  font-family:'Fira Code',Consolas,monospace; white-space:pre; line-height:1.55;
}
.msg-row.user .msg-text :deep(.ci-pre) {
  background:rgba(255,255,255,.12); border-color:rgba(255,255,255,.2);
}
.msg-text :deep(.ci-li) { display:block; padding-left:.2rem; line-height:1.8; }

@media(max-width:600px){
  .user-row { flex-wrap:wrap; }
  .msg-col { max-width:85%; }
}
</style>
