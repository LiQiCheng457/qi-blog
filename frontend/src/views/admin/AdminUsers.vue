<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { adminApi } from '@/api/admin'
import type { AdminUser, AdminUserUpdate } from '@/api/admin'
import { useUserStore } from '@/stores/user'
import { assetUrl } from '@/utils/assets'

const router    = useRouter()
const userStore = useUserStore()
const users     = ref<AdminUser[]>([])
const loading   = ref(true)
const search    = ref('')
const error     = ref('')

// ── Edit modal ──────────────────────────────────────────────────────────────
const editTarget = ref<AdminUser | null>(null)
const editForm   = reactive<AdminUserUpdate & { username: string; email: string }>({
  username: '', email: '', role: '', bio: '',
})
const editError = ref('')
const saving    = ref(false)

function openEdit(u: AdminUser) {
  editTarget.value = u
  editForm.username = u.username
  editForm.email    = u.email
  editForm.role     = u.role
  editForm.bio      = u.bio ?? ''
  editError.value   = ''
}

function closeEdit() {
  editTarget.value = null
}

async function saveEdit() {
  if (!editTarget.value) return
  saving.value    = true
  editError.value = ''
  try {
    const payload: AdminUserUpdate = {}
    const t = editTarget.value
    if (editForm.username !== t.username) payload.username = editForm.username
    if (editForm.email    !== t.email)    payload.email    = editForm.email
    if (editForm.role     !== t.role)     payload.role     = editForm.role
    payload.bio = editForm.bio || undefined

    await adminApi.editUser(t.id, payload)

    // 更新本地列表
    const idx = users.value.findIndex(u => u.id === t.id)
    if (idx !== -1) {
      users.value[idx] = {
        ...users.value[idx],
        username: editForm.username,
        email:    editForm.email,
        role:     editForm.role as string,
        bio:      editForm.bio || undefined,
      }
    }
    closeEdit()
  } catch (e: any) {
    editError.value = e.message ?? '保存失败'
  } finally {
    saving.value = false
  }
}

// ── Data ────────────────────────────────────────────────────────────────────
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(u =>
    u.username.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
  )
})

const regularUsers = computed(() => filtered.value.filter(u => u.role !== 'admin'))
const adminUsers   = computed(() => filtered.value.filter(u => u.role === 'admin'))

async function load() {
  loading.value = true
  try { users.value = await adminApi.listUsers() }
  catch (e: any) { error.value = e.message ?? '加载失败' }
  finally { loading.value = false }
}

onMounted(load)

function formatDate(s: string) {
  return new Date(s).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

async function deleteUser(u: AdminUser) {
  if (!confirm(`确定删除用户「${u.username}」？该用户的评论不会被自动删除。`)) return
  try {
    await adminApi.deleteUser(u.id)
    users.value = users.value.filter(x => x.id !== u.id)
  } catch (e: any) {
    alert(e.message ?? '删除失败')
  }
}

function viewComments(u: AdminUser) {
  router.push({ name: 'admin-comments', query: { userId: u.id, username: u.username } })
}
</script>

<template>
  <div class="admin-users">
    <div class="page-header">
      <div>
        <h1 class="page-title">用户管理</h1>
        <p class="page-sub">共 {{ users.length }} 位用户，其中 {{ adminUsers.length }} 位管理员</p>
      </div>
      <input v-model="search" class="search-input" type="text" placeholder="搜索用户名或邮箱…" />
    </div>

    <div v-if="error" class="err-msg">{{ error }}</div>
    <div v-else-if="loading" class="empty">加载中…</div>
    <template v-else>
      <!-- 管理员 -->
      <section v-if="adminUsers.length" class="user-section">
        <h2 class="section-label">管理员</h2>
        <div class="user-list">
          <div v-for="u in adminUsers" :key="u.id" class="user-row">
            <div class="user-avatar">
              <img v-if="u.avatar" :src="assetUrl(u.avatar)" :alt="u.username" />
              <span v-else class="avatar-fallback">{{ u.username[0] }}</span>
            </div>
            <div class="user-info">
              <div class="user-name-row">
                <span class="user-name">{{ u.username }}</span>
                <span v-if="u.id === userStore.profile?.id" class="self-tag">（我）</span>
                <span class="role-badge role-badge--admin">管理员</span>
              </div>
              <span class="user-email">{{ u.email }}</span>
              <span v-if="u.bio" class="user-bio">{{ u.bio }}</span>
            </div>
            <div class="user-actions">
              <button
                v-if="u.comment_count > 0"
                class="comment-count-btn"
                @click="viewComments(u)"
                title="查看该用户评论"
              >💬 {{ u.comment_count }}</button>
              <span v-else class="comment-count-zero">💬 0</span>
              <span class="user-date">{{ formatDate(u.created_at) }}</span>
              <button class="edit-btn" @click="openEdit(u)">编辑</button>
            </div>
          </div>
        </div>
      </section>

      <!-- 普通用户 -->
      <section class="user-section">
        <h2 class="section-label">普通用户 <span class="section-count">{{ regularUsers.length }}</span></h2>
        <div v-if="regularUsers.length === 0" class="empty">暂无普通用户</div>
        <div v-else class="user-list">
          <div v-for="u in regularUsers" :key="u.id" class="user-row">
            <div class="user-avatar">
              <img v-if="u.avatar" :src="assetUrl(u.avatar)" :alt="u.username" />
              <span v-else class="avatar-fallback">{{ u.username[0] }}</span>
            </div>
            <div class="user-info">
              <div class="user-name-row">
                <span class="user-name">{{ u.username }}</span>
                <span class="role-badge">读者</span>
              </div>
              <span class="user-email">{{ u.email }}</span>
              <span v-if="u.bio" class="user-bio">{{ u.bio }}</span>
            </div>
            <div class="user-actions">
              <button
                v-if="u.comment_count > 0"
                class="comment-count-btn"
                @click="viewComments(u)"
                title="查看该用户评论"
              >💬 {{ u.comment_count }}</button>
              <span v-else class="comment-count-zero">💬 0</span>
              <span class="user-date">{{ formatDate(u.created_at) }}</span>
              <button class="edit-btn" @click="openEdit(u)">编辑</button>
              <button class="del-btn" @click="deleteUser(u)">删除</button>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- 编辑弹窗 -->
    <Teleport to="body">
      <div v-if="editTarget" class="modal-overlay" @click.self="closeEdit">
        <div class="modal">
          <div class="modal-header">
            <h3 class="modal-title">编辑用户</h3>
            <button class="modal-close" @click="closeEdit">×</button>
          </div>

          <div class="modal-body">
            <div class="user-preview">
              <div class="preview-avatar">
                <img v-if="editTarget.avatar" :src="assetUrl(editTarget.avatar)" :alt="editTarget.username" />
                <span v-else class="avatar-fallback">{{ editTarget.username[0] }}</span>
              </div>
              <div>
                <div class="preview-name">{{ editTarget.username }}</div>
                <div class="preview-id">ID: {{ editTarget.id }}</div>
              </div>
            </div>

            <div class="field">
              <label>用户名</label>
              <input v-model="editForm.username" type="text" class="field-input" />
            </div>
            <div class="field">
              <label>邮箱</label>
              <input v-model="editForm.email" type="email" class="field-input" />
            </div>
            <div class="field">
              <label>
                角色
                <span v-if="editTarget.id === userStore.profile?.id" class="field-hint">（不能修改自己的角色）</span>
              </label>
              <select
                v-model="editForm.role"
                class="field-input"
                :disabled="editTarget.id === userStore.profile?.id"
              >
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
            </div>
            <div class="field">
              <label>个人简介</label>
              <textarea v-model="editForm.bio" class="field-input field-textarea" rows="3" placeholder="暂无简介" />
            </div>

            <div v-if="editError" class="edit-error">{{ editError }}</div>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="closeEdit">取消</button>
            <button class="btn-save" :disabled="saving" @click="saveEdit">
              {{ saving ? '保存中…' : '保存修改' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.admin-users { width: 100%; }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; margin-bottom:2rem; flex-wrap:wrap; }
.page-title { font-family:'Noto Serif SC',serif; font-size:28px; font-weight:500; color:var(--qi-ink); margin-bottom:.25rem; }
.page-sub { font-size:13px; color:var(--qi-ink-muted); }
.search-input {
  padding:8px 14px; border-radius:8px; border:1.5px solid var(--qi-border);
  background:var(--qi-bg); font-size:13.5px; color:var(--qi-ink); outline:none;
  width:220px; font-family:inherit;
}
.search-input:focus { border-color:var(--qi-primary); }
.err-msg { color:#e05050; font-size:13.5px; }
.empty { color:var(--qi-ink-light); font-size:14px; padding:2rem 0; }

.user-section { margin-bottom:2rem; }
.section-label { font-size:12px; font-weight:600; color:var(--qi-ink-muted); text-transform:uppercase; letter-spacing:.06em; margin-bottom:.6rem; display:flex; align-items:center; gap:.4rem; }
.section-count { font-size:11px; background:var(--qi-bg-muted); color:var(--qi-ink-light); border-radius:999px; padding:1px 7px; font-weight:500; }

.user-list { display:flex; flex-direction:column; gap:.4rem; }
.user-row {
  display:flex; align-items:center; gap:.9rem;
  background:var(--qi-bg-card); border:1px solid var(--qi-border);
  border-radius:12px; padding:.75rem 1rem;
  transition: border-color .15s;
}
.user-row:hover { border-color:var(--qi-primary-light, rgba(255,140,90,.3)); }

.user-avatar { flex-shrink:0; width:40px; height:40px; border-radius:50%; overflow:hidden; border:1px solid var(--qi-border); }
.user-avatar img { width:100%; height:100%; object-fit:cover; }
.avatar-fallback {
  width:100%; height:100%; display:flex; align-items:center; justify-content:center;
  background:var(--qi-bg-muted); font-size:15px; font-weight:600; color:var(--qi-primary);
}

.user-info { flex:1; min-width:0; display:flex; flex-direction:column; gap:.2rem; }
.user-name-row { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; }
.user-name { font-size:14px; font-weight:500; color:var(--qi-ink); }
.self-tag { font-size:11px; color:var(--qi-ink-light); }
.user-email { font-size:12px; color:var(--qi-ink-light); }
.user-bio { font-size:12px; color:var(--qi-ink-muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

.role-badge {
  flex-shrink:0; font-size:10px; font-weight:600; padding:2px 8px; border-radius:999px;
  background:rgba(168,216,192,.25); color:#5A9E82;
}
.role-badge--admin { background:rgba(255,140,90,.12); color:var(--qi-primary); }

.user-actions { display:flex; align-items:center; gap:.5rem; flex-shrink:0; }
.comment-count-btn {
  font-size:12px; padding:3px 9px; border-radius:6px;
  border:1px solid var(--qi-border); background:var(--qi-bg-muted);
  color:var(--qi-ink-muted); cursor:pointer; transition:all .15s; white-space:nowrap;
}
.comment-count-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); background:rgba(255,140,90,.06); }
.comment-count-zero { font-size:12px; color:var(--qi-border); padding:3px 9px; }
.user-date { flex-shrink:0; font-size:12px; color:var(--qi-ink-light); white-space:nowrap; }

.edit-btn {
  font-size:12px; padding:4px 12px; border-radius:6px;
  border:1px solid var(--qi-border); background:transparent;
  color:var(--qi-ink-muted); cursor:pointer; transition:all .15s;
}
.edit-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); }
.del-btn {
  font-size:12px; padding:4px 10px; border-radius:6px;
  border:none; background:transparent; color:#e05050; cursor:pointer; transition:background .15s;
}
.del-btn:hover { background:rgba(224,80,80,.08); }

/* ── 编辑弹窗 ── */
.modal-overlay {
  position:fixed; inset:0; z-index:1000;
  background:rgba(0,0,0,.45); backdrop-filter:blur(3px);
  display:flex; align-items:center; justify-content:center; padding:1rem;
}
.modal {
  background:var(--qi-bg-card); border:1px solid var(--qi-border); border-radius:16px;
  width:100%; max-width:460px; box-shadow:0 20px 60px rgba(0,0,0,.2);
  display:flex; flex-direction:column; max-height:90vh; overflow:hidden;
}
.modal-header {
  display:flex; align-items:center; justify-content:space-between;
  padding:1.25rem 1.5rem .9rem; border-bottom:1px solid var(--qi-border);
}
.modal-title { font-size:16px; font-weight:600; color:var(--qi-ink); margin:0; }
.modal-close {
  all:unset; cursor:pointer; font-size:20px; color:var(--qi-ink-muted); line-height:1;
  padding:2px 6px; border-radius:4px; transition:color .15s;
}
.modal-close:hover { color:var(--qi-ink); }

.modal-body { padding:1.25rem 1.5rem; overflow-y:auto; display:flex; flex-direction:column; gap:1rem; }

.user-preview { display:flex; align-items:center; gap:.75rem; padding:.75rem; background:var(--qi-bg-muted); border-radius:10px; }
.preview-avatar { width:40px; height:40px; border-radius:50%; overflow:hidden; border:1px solid var(--qi-border); flex-shrink:0; }
.preview-avatar img { width:100%; height:100%; object-fit:cover; }
.preview-name { font-size:14px; font-weight:500; color:var(--qi-ink); }
.preview-id { font-size:12px; color:var(--qi-ink-light); }

.field { display:flex; flex-direction:column; gap:.4rem; }
.field label { font-size:12px; font-weight:600; color:var(--qi-ink-muted); display:flex; align-items:center; gap:.4rem; }
.field-hint { font-size:11px; color:var(--qi-ink-light); font-weight:400; }
.field-input {
  padding:8px 12px; border-radius:8px; border:1.5px solid var(--qi-border);
  background:var(--qi-bg); font-size:13.5px; color:var(--qi-ink);
  outline:none; font-family:inherit; transition:border-color .15s;
}
.field-input:focus { border-color:var(--qi-primary); }
.field-input:disabled { opacity:.5; cursor:not-allowed; }
.field-textarea { resize:vertical; min-height:72px; }

.edit-error { font-size:13px; color:#e05050; background:rgba(224,80,80,.06); border-radius:8px; padding:.5rem .75rem; }

.modal-footer {
  display:flex; gap:.75rem; justify-content:flex-end;
  padding:.9rem 1.5rem 1.25rem; border-top:1px solid var(--qi-border);
}
.btn-cancel {
  padding:8px 18px; border-radius:8px; border:1.5px solid var(--qi-border);
  background:transparent; color:var(--qi-ink-muted); font-size:13.5px; cursor:pointer;
  font-family:inherit; transition:all .15s;
}
.btn-cancel:hover { border-color:var(--qi-ink-muted); color:var(--qi-ink); }
.btn-save {
  padding:8px 20px; border-radius:8px; border:none;
  background:var(--qi-primary); color:#fff; font-size:13.5px; cursor:pointer;
  font-family:inherit; transition:opacity .15s; font-weight:500;
}
.btn-save:hover { opacity:.88; }
.btn-save:disabled { opacity:.5; cursor:not-allowed; }

@media(max-width:640px){
  .user-row { flex-wrap:wrap; }
  .user-date { display:none; }
  .user-actions { flex-wrap:wrap; }
}
</style>
