<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { commentsApi, type Comment } from '@/api/comments'
import { useUserStore } from '@/stores/user'
import UserAuthModal from './UserAuthModal.vue'

const props = defineProps<{ postSlug: string }>()

const userStore  = useUserStore()
const comments   = ref<Comment[]>([])
const loading    = ref(true)
const sending    = ref(false)
const newContent = ref('')
const replyTo    = ref<Comment | null>(null)
const showAuth   = ref(false)
const error      = ref('')

onMounted(async () => {
  try { comments.value = await commentsApi.list(props.postSlug) }
  finally { loading.value = false }
})

// 顶层评论
const topComments = computed(() => comments.value.filter(c => !c.parentId))
// 回复列表
function repliesOf(id: number) { return comments.value.filter(c => c.parentId === id) }

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' })
}

async function send() {
  if (!newContent.value.trim()) return
  if (!userStore.isLoggedIn) { showAuth.value = true; return }
  error.value = ''
  sending.value = true
  try {
    const c = await commentsApi.create(props.postSlug, newContent.value.trim(), replyTo.value?.id)
    comments.value.push(c)
    newContent.value = ''
    replyTo.value = null
  } catch (e: any) {
    error.value = e.message ?? '发送失败'
  } finally {
    sending.value = false
  }
}

async function remove(id: number) {
  if (!confirm('确定删除这条评论？')) return
  try {
    if (userStore.isAdmin) {
      await commentsApi.adminDelete(id)
    } else {
      await commentsApi.delete(id)
    }
    comments.value = comments.value.filter(c => c.id !== id)
  } catch (e: any) {
    error.value = e.message ?? '删除失败'
  }
}

function canDelete(c: Comment) {
  return userStore.isAdmin || (userStore.isLoggedIn && userStore.profile?.id === c.userId)
}
</script>

<template>
  <section class="comments">
    <h2 class="comments-title">
      评论 <span class="count">{{ comments.length }}</span>
    </h2>

    <!-- 输入框 -->
    <div class="comment-form">
      <div v-if="replyTo" class="reply-hint">
        回复 <strong>{{ replyTo.username }}</strong>：{{ replyTo.content.slice(0, 30) }}{{ replyTo.content.length > 30 ? '…' : '' }}
        <button @click="replyTo = null" class="cancel-reply">取消</button>
      </div>
      <div class="input-row">
        <div class="user-avatar-sm">
          {{ userStore.profile?.username?.[0]?.toUpperCase() ?? '？' }}
        </div>
        <textarea
          v-model="newContent"
          class="comment-input"
          :placeholder="userStore.isLoggedIn ? (replyTo ? `回复 ${replyTo.username}…` : '写下你的想法…') : '登录后参与讨论'"
          rows="3"
          @keydown.ctrl.enter="send"
        ></textarea>
      </div>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <div class="form-footer">
        <span v-if="userStore.isLoggedIn" class="logged-as">
          以 <strong>{{ userStore.profile?.username }}</strong> 身份发言
          <button class="logout-link" @click="userStore.logout()">退出</button>
        </span>
        <button v-else class="login-tip" @click="showAuth = true">登录 / 注册后发言</button>
        <button class="send-btn" :disabled="sending || !newContent.trim()" @click="send">
          {{ sending ? '发送中…' : 'Ctrl+Enter 发送' }}
        </button>
      </div>
    </div>

    <!-- 评论列表 -->
    <div v-if="loading" class="empty">加载评论中…</div>
    <div v-else-if="topComments.length === 0" class="empty">还没有评论，来做第一个留言的人吧 🐾</div>
    <div v-else class="comment-list">
      <div v-for="c in topComments" :key="c.id" class="comment-item">
        <div class="avatar">{{ c.username[0]?.toUpperCase() }}</div>
        <div class="comment-body">
          <div class="comment-meta">
            <span class="c-name">{{ c.username }}</span>
            <span v-if="c.role === 'admin'" class="c-admin-badge">博主</span>
            <span class="c-time">{{ formatDate(c.createdAt) }}</span>
          </div>
          <p class="c-content">{{ c.content }}</p>
          <div class="comment-actions">
            <button class="action-link" @click="replyTo = c">回复</button>
            <button v-if="canDelete(c)" class="action-link danger" @click="remove(c.id)">删除</button>
          </div>

          <!-- 子回复 -->
          <div v-for="r in repliesOf(c.id)" :key="r.id" class="reply-item">
            <div class="avatar avatar--sm">{{ r.username[0]?.toUpperCase() }}</div>
            <div class="comment-body">
              <div class="comment-meta">
                <span class="c-name">{{ r.username }}</span>
                <span class="c-time">{{ formatDate(r.createdAt) }}</span>
              </div>
              <p class="c-content">{{ r.content }}</p>
              <div class="comment-actions">
                <button class="action-link" @click="replyTo = r">回复</button>
                <button v-if="canDelete(r)" class="action-link danger" @click="remove(r.id)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 登录/注册弹窗 -->
    <Teleport to="body">
      <UserAuthModal v-if="showAuth" @close="showAuth = false" />
    </Teleport>
  </section>
</template>

<style scoped>
.comments { margin-top:4rem; padding-top:3rem; border-top:1px solid var(--qi-border); }
.comments-title { font-family:'Noto Serif SC',serif; font-size:22px; font-weight:500; color:var(--qi-ink); margin-bottom:1.5rem; }
.count { font-size:16px; color:var(--qi-ink-light); font-family:'Inter',sans-serif; font-weight:400; }

/* 输入区 */
.comment-form { background:var(--qi-bg-card); border:1.5px solid var(--qi-border); border-radius:16px; padding:1.25rem; margin-bottom:2rem; }
.reply-hint { font-size:13px; color:var(--qi-ink-muted); background:rgba(255,140,90,.08); border-radius:8px; padding:.5rem .875rem; margin-bottom:.875rem; display:flex; align-items:center; gap:.5rem; }
.cancel-reply { font-size:12px; color:var(--qi-ink-light); background:none; border:none; cursor:pointer; margin-left:auto; }
.cancel-reply:hover { color:var(--qi-primary); }
.input-row { display:flex; gap:.75rem; align-items:flex-start; }
.user-avatar-sm { width:34px; height:34px; border-radius:50%; background:var(--qi-primary); color:white; font-size:14px; font-weight:600; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.comment-input { flex:1; border:1.5px solid var(--qi-border); border-radius:10px; padding:.75rem 1rem; font-size:14px; color:var(--qi-ink); background:var(--qi-bg); resize:none; outline:none; font-family:inherit; line-height:1.6; transition:border-color .2s; }
.comment-input:focus { border-color:var(--qi-primary); }
.comment-input::placeholder { color:var(--qi-ink-light); }
.form-footer { display:flex; align-items:center; justify-content:space-between; margin-top:.875rem; flex-wrap:wrap; gap:.5rem; }
.logged-as { font-size:13px; color:var(--qi-ink-muted); }
.logout-link { font-size:12px; color:var(--qi-ink-light); background:none; border:none; cursor:pointer; margin-left:.35rem; }
.logout-link:hover { color:#e05050; }
.login-tip { font-size:13px; color:var(--qi-primary); background:none; border:none; cursor:pointer; font-weight:500; }
.send-btn { padding:7px 18px; border-radius:999px; background:var(--qi-primary); color:white; font-size:13px; font-weight:500; border:none; cursor:pointer; transition:opacity .2s; }
.send-btn:hover:not(:disabled) { opacity:.88; }
.send-btn:disabled { opacity:.5; cursor:not-allowed; }
.error-msg { font-size:13px; color:#e05050; margin:.5rem 0 0; }

/* 列表 */
.comment-list { display:flex; flex-direction:column; gap:1.5rem; }
.comment-item { display:flex; gap:.875rem; }
.avatar { width:38px; height:38px; border-radius:50%; background:linear-gradient(135deg,var(--qi-primary),#a8d8c0); color:white; font-size:16px; font-weight:600; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.avatar--sm { width:30px; height:30px; font-size:13px; }
.comment-body { flex:1; min-width:0; }
.comment-meta { display:flex; align-items:baseline; gap:.625rem; margin-bottom:.375rem; }
.c-name { font-size:14px; font-weight:600; color:var(--qi-ink); }
.c-admin-badge { font-size:10px; font-weight:700; padding:1px 6px; border-radius:999px; background:rgba(255,140,90,.15); color:var(--qi-primary); border:1px solid rgba(255,140,90,.3); margin-left:.3rem; vertical-align:middle; }
.c-time { font-size:12px; color:var(--qi-ink-light); }
.c-content { font-size:14px; color:var(--qi-ink-muted); line-height:1.7; margin:0 0 .375rem; white-space:pre-wrap; word-break:break-word; }
.comment-actions { display:flex; gap:.875rem; }
.action-link { font-size:12px; color:var(--qi-ink-light); background:none; border:none; cursor:pointer; padding:0; transition:color .15s; }
.action-link:hover { color:var(--qi-primary); }
.action-link.danger:hover { color:#e05050; }
.reply-item { display:flex; gap:.625rem; margin-top:1rem; padding-top:1rem; border-top:1px solid var(--qi-border); }
.empty { text-align:center; padding:2.5rem 0; color:var(--qi-ink-light); font-size:14px; }
</style>
