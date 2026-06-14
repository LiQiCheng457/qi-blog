<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { api } from '@/api/client'

const avatarOptions = [
  { label: '专注敲代码', value: '/avatars/qi-avatar-coding.png' },
  { label: '醒来伸懒腰', value: '/avatars/qi-avatar-wake.png' },
  { label: '起风了', value: '/avatars/qi-avatar-wind.png' },
  { label: '抬头打招呼', value: '/avatars/qi-avatar-wave.png' },
  { label: '若有所思', value: '/avatars/qi-avatar-think.png' },
] as const

const allowedAvatars = new Set<string>(avatarOptions.map(option => option.value))

const user     = useUserStore()
const saving   = ref(false)
const success  = ref(false)
const errorMsg = ref('')

const form = reactive<{ username: string; bio: string; avatar: string }>({
  username: '',
  bio:      '',
  avatar:   avatarOptions[0].value,
})

const roleLabel = computed(() => user.isAdmin ? '博主' : '读者')
const profileName = computed(() => user.profile?.username ?? '未登录用户')
const profileEmail = computed(() => user.profile?.email ?? '')
const selectedAvatar = computed(() => (
  allowedAvatars.has(form.avatar) ? form.avatar : avatarOptions[0].value
))

watch(
  () => user.profile,
  profile => {
    form.username = profile?.username ?? ''
    form.bio = profile?.bio ?? ''
    form.avatar = profile?.avatar && allowedAvatars.has(profile.avatar)
      ? profile.avatar
      : avatarOptions[0].value
  },
  { immediate: true },
)

function selectAvatar(value: string) {
  form.avatar = value
}

async function save() {
  saving.value = true
  success.value = false
  errorMsg.value = ''
  try {
    await user.updateProfile({
      username: form.username.trim() || undefined,
      bio:      form.bio.trim()      || undefined,
      avatar:   selectedAvatar.value,
    })
    success.value = true
    setTimeout(() => { success.value = false }, 3000)
  } catch (e: any) {
    errorMsg.value = e.message ?? '保存失败'
  } finally {
    saving.value = false
  }
}

const pwdForm = reactive({ old: '', newPwd: '', confirm: '' })
const pwdSaving  = ref(false)
const pwdSuccess = ref(false)
const pwdError   = ref('')

async function changePassword() {
  pwdError.value   = ''
  pwdSuccess.value = false
  if (pwdForm.newPwd.length < 6) { pwdError.value = '新密码至少 6 位'; return }
  if (pwdForm.newPwd !== pwdForm.confirm) { pwdError.value = '两次密码不一致'; return }
  pwdSaving.value = true
  try {
    await api.patch('/api/users/password', { old_password: pwdForm.old, new_password: pwdForm.newPwd })
    pwdSuccess.value = true
    pwdForm.old = pwdForm.newPwd = pwdForm.confirm = ''
    setTimeout(() => { pwdSuccess.value = false }, 3000)
  } catch (e: any) {
    pwdError.value = e.message ?? '修改失败'
  } finally {
    pwdSaving.value = false
  }
}
</script>

<template>
  <div class="profile-page">
    <section class="profile-shell">
      <header class="profile-header">
        <div class="profile-identity">
          <div class="avatar-stage">
            <img :src="selectedAvatar" :alt="`${profileName} 的头像`" class="avatar-main" />
          </div>
          <div class="identity-copy">
            <span class="role-pill" :class="user.isAdmin ? 'admin' : 'reader'">{{ roleLabel }}</span>
            <h1>{{ profileName }}</h1>
            <p>{{ profileEmail }}</p>
          </div>
        </div>
        <div class="profile-note">
          <span>头像库</span>
          <strong>5</strong>
          <span>个固定形象</span>
        </div>
      </header>

      <div class="profile-content">
        <form class="profile-section profile-form" @submit.prevent="save">
          <div class="section-heading">
            <h2>个人资料</h2>
            <p>更新展示名称、简介和站内头像。</p>
          </div>

          <div class="avatar-field">
            <label>选择头像</label>
            <div class="avatar-grid" role="radiogroup" aria-label="选择头像">
              <button
                v-for="option in avatarOptions"
                :key="option.value"
                class="avatar-option"
                :class="{ selected: selectedAvatar === option.value }"
                type="button"
                role="radio"
                :aria-checked="selectedAvatar === option.value"
                @click="selectAvatar(option.value)"
              >
                <img :src="option.value" :alt="option.label" />
                <span>{{ option.label }}</span>
              </button>
            </div>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="profile-username">用户名</label>
              <input id="profile-username" v-model="form.username" type="text" placeholder="2-20 个字符" minlength="2" maxlength="20" />
            </div>
          </div>

          <div class="field">
            <label for="profile-bio">个人简介</label>
            <textarea id="profile-bio" v-model="form.bio" rows="5" placeholder="简单介绍一下自己..." maxlength="200" />
            <span class="field-hint">{{ form.bio.length }} / 200</span>
          </div>

          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
          <p v-if="success" class="success-msg">保存成功</p>

          <button type="submit" class="primary-btn" :disabled="saving">
            {{ saving ? '保存中...' : '保存修改' }}
          </button>
        </form>

        <form class="profile-section password-form" @submit.prevent="changePassword">
          <div class="section-heading">
            <h2>修改密码</h2>
            <p>确认当前密码后设置新密码。</p>
          </div>

          <div class="field">
            <label for="current-password">当前密码</label>
            <input id="current-password" v-model="pwdForm.old" type="password" placeholder="输入当前密码" required />
          </div>
          <div class="field">
            <label for="new-password">新密码</label>
            <input id="new-password" v-model="pwdForm.newPwd" type="password" placeholder="至少 6 位" required />
          </div>
          <div class="field">
            <label for="confirm-password">确认新密码</label>
            <input id="confirm-password" v-model="pwdForm.confirm" type="password" placeholder="再次输入新密码" required />
          </div>

          <p v-if="pwdError" class="error-msg">{{ pwdError }}</p>
          <p v-if="pwdSuccess" class="success-msg">密码修改成功</p>

          <button type="submit" class="secondary-btn" :disabled="pwdSaving">
            {{ pwdSaving ? '修改中...' : '确认修改密码' }}
          </button>
        </form>
      </div>
    </section>
  </div>
</template>

<style scoped>
.profile-page {
  height: 100vh;
  min-height: 760px;
  padding: 84px 1.5rem 18px;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 12%, rgba(255, 209, 102, 0.12), transparent 28rem),
    var(--qi-bg);
}

.profile-shell {
  width: min(1040px, 100%);
  margin: 0 auto;
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  padding: .8rem 0 1.15rem;
  border-bottom: 1px solid var(--qi-border);
}

.profile-identity {
  display: flex;
  align-items: center;
  gap: 1.35rem;
  min-width: 0;
}

.avatar-stage {
  width: 92px;
  height: 92px;
  border-radius: 16px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-card);
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 10px 30px var(--qi-shadow);
}

.avatar-main {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.identity-copy {
  min-width: 0;
}

.identity-copy h1 {
  margin: .3rem 0 .15rem;
  font-family: 'Noto Serif SC', serif;
  font-size: 30px;
  font-weight: 500;
  line-height: 1.25;
  color: var(--qi-ink);
}

.identity-copy p {
  font-size: 14px;
  color: var(--qi-ink-muted);
}

.role-pill {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(168, 216, 192, .18);
  color: #3a8c6a;
}

.role-pill.admin {
  background: rgba(255, 140, 90, .14);
  color: var(--qi-primary);
}

.profile-note {
  display: grid;
  grid-template-columns: auto auto auto;
  align-items: baseline;
  gap: .45rem;
  color: var(--qi-ink-muted);
  white-space: nowrap;
}

.profile-note strong {
  font-family: 'Noto Serif SC', serif;
  font-size: 34px;
  line-height: 1;
  color: var(--qi-primary);
}

.profile-content {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(280px, .65fr);
  gap: 1.5rem;
  padding-top: 1.5rem;
  align-items: start;
}

.profile-section {
  border: 1.5px solid var(--qi-border);
  border-radius: 16px;
  background: color-mix(in srgb, var(--qi-bg-card) 86%, transparent);
  padding: 1.15rem;
}

.section-heading {
  margin-bottom: .9rem;
}

.section-heading h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--qi-ink);
  margin-bottom: .25rem;
}

.section-heading p {
  font-size: 13px;
  color: var(--qi-ink-light);
}

.profile-form,
.password-form {
  display: flex;
  flex-direction: column;
  gap: .85rem;
}

.avatar-field {
  display: flex;
  flex-direction: column;
  gap: .5rem;
}

.avatar-field > label,
.field label {
  font-size: 13px;
  font-weight: 700;
  color: var(--qi-ink-muted);
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: .55rem;
}

.avatar-option {
  min-width: 0;
  border: 1.5px solid var(--qi-border);
  border-radius: 12px;
  background: var(--qi-bg);
  color: var(--qi-ink-muted);
  padding: .35rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: .3rem;
  transition: border-color .2s, color .2s, transform .2s, box-shadow .2s;
}

.avatar-option:hover,
.avatar-option.selected {
  border-color: var(--qi-primary);
  color: var(--qi-primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px var(--qi-shadow);
}

.avatar-option img {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  object-fit: cover;
  display: block;
  background: white;
}

.avatar-option span {
  width: 100%;
  font-size: 11px;
  line-height: 1.25;
  text-align: center;
  overflow-wrap: anywhere;
}

.field-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: .32rem;
}

.field input,
.field textarea {
  width: 100%;
  padding: 9px 13px;
  border-radius: 10px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg);
  font-size: 14px;
  color: var(--qi-ink);
  outline: none;
  transition: border-color .2s, box-shadow .2s;
  resize: vertical;
  font-family: inherit;
}

.field textarea {
  height: 92px;
  resize: none;
}

.field input:focus,
.field textarea:focus {
  border-color: var(--qi-primary);
  box-shadow: 0 0 0 3px rgba(255, 140, 90, .12);
}

.field-hint {
  font-size: 12px;
  color: var(--qi-ink-light);
}

.error-msg,
.success-msg {
  font-size: 13px;
  border-radius: 10px;
  padding: .55rem .75rem;
  margin: 0;
}

.error-msg {
  color: #e05050;
  background: rgba(224, 80, 80, .06);
  border: 1px solid rgba(224, 80, 80, .2);
}

.success-msg {
  color: #3a8c6a;
  background: rgba(168, 216, 192, .15);
  border: 1px solid rgba(168, 216, 192, .4);
}

.primary-btn,
.secondary-btn {
  min-height: 40px;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  font-size: 15px;
  font-weight: 700;
  transition: opacity .2s, transform .2s;
}

.primary-btn {
  background: var(--qi-primary);
  color: white;
}

.secondary-btn {
  background: var(--qi-bg);
  color: var(--qi-primary);
  border: 1.5px solid var(--qi-border);
}

.primary-btn:hover:not(:disabled),
.secondary-btn:hover:not(:disabled) {
  opacity: .9;
  transform: translateY(-1px);
}

.primary-btn:disabled,
.secondary-btn:disabled {
  opacity: .6;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .profile-page {
    height: auto;
    min-height: 100vh;
    overflow: visible;
  }

  .profile-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .profile-page {
    padding: 88px 1rem 3rem;
  }

  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-note {
    display: none;
  }

  .avatar-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .identity-copy h1 {
    font-size: 28px;
  }
}

@media (max-width: 420px) {
  .profile-identity {
    align-items: flex-start;
  }

  .avatar-stage {
    width: 88px;
    height: 88px;
  }
}
</style>
