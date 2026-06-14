<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsApi } from '@/api/posts'
import MarkdownEditor from '@/components/MarkdownEditor.vue'

const route  = useRoute()
const router = useRouter()

const slug = computed(() => route.params.slug as string | undefined)
const isNew = computed(() => !slug.value || slug.value === 'new' || route.path.endsWith('/new'))

const loading  = ref(false)
const saving   = ref(false)
const error    = ref('')

const form = ref({
  slug:         '',
  title:        '',
  summary:      '',
  content:      '',
  tags:         '',
  cover:        '',
  readingTime:  3,
})

onMounted(async () => {
  if (isNew.value) return
  loading.value = true
  try {
    const post = await postsApi.get(slug.value!)
    form.value = {
      slug:        post.slug,
      title:       post.title,
      summary:     post.summary,
      content:     post.content,
      tags:        post.tags.join(', '),
      cover:       post.cover ?? '',
      readingTime: post.readingTime,
    }
  } catch {
    error.value = '文章加载失败'
  } finally {
    loading.value = false
  }
})

async function save() {
  error.value = ''
  if (!form.value.title.trim()) { error.value = '标题不能为空'; return }
  if (!form.value.slug.trim() && isNew.value) { error.value = 'Slug 不能为空'; return }
  saving.value = true
  try {
    const payload = {
      title:        form.value.title.trim(),
      summary:      form.value.summary.trim(),
      content:      form.value.content,
      tags:         form.value.tags.split(',').map(t => t.trim()).filter(Boolean).join(','),
      cover:        form.value.cover.trim() || undefined,
      reading_time: form.value.readingTime,
      published:    true,
    }
    if (isNew.value) {
      await postsApi.create({ ...payload, slug: form.value.slug.trim() })
    } else {
      await postsApi.update(slug.value!, payload)
    }
    router.push('/admin/posts')
  } catch (e: any) {
    error.value = e.message ?? '保存失败'
  } finally {
    saving.value = false
  }
}

function autoSlug() {
  if (!isNew.value || form.value.slug) return
  form.value.slug = form.value.title
    .toLowerCase()
    .replace(/[\s一-龥]+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}
</script>

<template>
  <div class="post-edit">
    <div class="page-header">
      <h1 class="page-title">{{ isNew ? '写新文章' : '编辑文章' }}</h1>
      <div class="header-actions">
        <RouterLink to="/admin/posts" class="cancel-btn">取消</RouterLink>
        <button class="save-btn" :disabled="saving" @click="save">
          {{ saving ? '保存中…' : '保存发布' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else class="edit-form">
      <p v-if="error" class="error-msg">{{ error }}</p>

      <div class="meta-grid">
        <div class="field field--full">
          <label>文章标题 *</label>
          <input v-model="form.title" type="text" placeholder="起一个好标题…" @blur="autoSlug" />
        </div>

        <div class="field">
          <label>Slug（URL 标识）{{ isNew ? ' *' : '' }}</label>
          <input v-model="form.slug" type="text" placeholder="e.g. my-first-post"
            :disabled="!isNew" :class="{disabled:!isNew}" />
        </div>

        <div class="field">
          <label>阅读时间（分钟）</label>
          <input v-model.number="form.readingTime" type="number" min="1" max="120" />
        </div>

        <div class="field field--full">
          <label>摘要</label>
          <textarea v-model="form.summary" rows="2" placeholder="一两句话描述文章内容…"></textarea>
        </div>

        <div class="field field--full">
          <label>标签（逗号分隔）</label>
          <input v-model="form.tags" type="text" placeholder="Vue, TypeScript, 前端" />
        </div>

        <div class="field field--full">
          <label>封面图 URL（可选）</label>
          <input v-model="form.cover" type="url" placeholder="https://…" />
        </div>
      </div>

      <div class="field field--full">
        <label>正文内容</label>
        <MarkdownEditor v-model="form.content" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-edit { width:100%; }
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:2rem; gap:1rem; }
.page-title { font-family:'Noto Serif SC',serif; font-size:26px; font-weight:500; color:var(--qi-ink); }
.header-actions { display:flex; gap:.75rem; align-items:center; }
.cancel-btn { font-size:14px; color:var(--qi-ink-muted); text-decoration:none; padding:8px 16px; border-radius:999px; border:1.5px solid var(--qi-border); }
.cancel-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); }
.save-btn { padding:9px 22px; border-radius:999px; background:var(--qi-primary); color:white; font-size:14px; font-weight:500; border:none; cursor:pointer; }
.save-btn:hover:not(:disabled) { opacity:.88; }
.save-btn:disabled { opacity:.6; cursor:not-allowed; }
.loading { color:var(--qi-ink-light); font-size:14px; }
.error-msg { font-size:13px; color:#e05050; margin-bottom:1rem; background:rgba(224,80,80,.06); border:1px solid rgba(224,80,80,.2); border-radius:8px; padding:.75rem 1rem; }
.meta-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.5rem; }
.field { display:flex; flex-direction:column; gap:.4rem; }
.field--full { grid-column:1 / -1; }
.field label { font-size:13px; font-weight:500; color:var(--qi-ink-muted); }
.field input,.field textarea { padding:9px 14px; border-radius:10px; border:1.5px solid var(--qi-border); background:var(--qi-bg-card); font-size:14px; color:var(--qi-ink); outline:none; transition:border-color .2s; font-family:inherit; }
.field input:focus,.field textarea:focus { border-color:var(--qi-primary); }
.field input.disabled { opacity:.6; cursor:not-allowed; }
.field textarea { resize:vertical; line-height:1.6; }
@media(max-width:600px){
  .meta-grid{grid-template-columns:1fr;}
  .page-header{flex-direction:column;align-items:flex-start;}
}
</style>
