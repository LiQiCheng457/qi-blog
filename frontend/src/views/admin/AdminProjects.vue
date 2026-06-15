<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { projectsApi } from '@/api/projects'
import { exesApi } from '@/api/exes'
import type { ExeFile } from '@/api/exes'
import type { Project } from '@/types'
import ImagePickerModal from '@/components/ImagePickerModal.vue'

type ProjectStatus = Project['status']
type ProjectForm = {
  name: string
  description: string
  techStack: string
  link: string
  githubUrl: string
  downloadUrl: string
  cover: string
  category: string
  featured: boolean
  status: ProjectStatus
}

const projects = ref<Project[]>([])
const loading  = ref(true)
const showForm = ref(false)
const saving   = ref(false)
const editId   = ref<number | null>(null)
const error    = ref('')

const showImagePicker = ref(false)
const showExePicker   = ref(false)
const exeFiles        = ref<ExeFile[]>([])
const exePickerLoaded = ref(false)

async function openExePicker() {
  showExePicker.value = true
  if (!exePickerLoaded.value) {
    try { exeFiles.value = await exesApi.list() }
    finally { exePickerLoaded.value = true }
  }
}

const blankForm = (): ProjectForm => ({
  name: '', description: '', techStack: '', link: '',
  githubUrl: '', downloadUrl: '', cover: '', category: '全栈', featured: false, status: 'active',
})
const form = ref(blankForm())

async function load() {
  loading.value = true
  try { projects.value = await projectsApi.list() } finally { loading.value = false }
}

onMounted(load)

function openNew() {
  editId.value = null
  form.value = blankForm()
  showForm.value = true
}

function openEdit(p: Project) {
  editId.value = p.id
  form.value = {
    name: p.name, description: p.description,
    techStack: p.techStack.join(', '),
    link: p.link ?? '', githubUrl: p.githubUrl ?? '',
    downloadUrl: p.download ?? '',
    cover: p.cover ?? '',
    category: p.category, featured: p.featured, status: p.status,
  }
  showForm.value = true
}

async function saveProject() {
  error.value = ''
  if (!form.value.name.trim()) { error.value = '项目名称不能为空'; return }
  saving.value = true
  try {
    const payload = {
      name: form.value.name.trim(),
      description: form.value.description.trim(),
      tech_stack: form.value.techStack.split(',').map(t => t.trim()).filter(Boolean).join(','),
      url: form.value.link.trim() || null,
      github: form.value.githubUrl.trim() || null,
      download: form.value.downloadUrl.trim() || null,
      cover: form.value.cover.trim() || null,
      category: form.value.category,
      featured: form.value.featured,
      status: form.value.status,
    }
    if (editId.value) {
      await projectsApi.update(editId.value, payload)
    } else {
      const slug = form.value.name.toLowerCase()
        .replace(/[\s一-鿿]+/g, '-')
        .replace(/[^a-z0-9-]/g, '')
        .replace(/-+/g, '-').replace(/^-|-$/g, '') || `project-${Date.now()}`
      await projectsApi.create({ ...payload, project_id: slug })
    }
    await load()
    showForm.value = false
  } catch (e: any) {
    error.value = e.message ?? '保存失败'
  } finally {
    saving.value = false
  }
}

async function deleteProject(id: number, name: string) {
  if (!confirm(`确定删除「${name}」？`)) return
  await projectsApi.delete(id)
  projects.value = projects.value.filter(p => p.id !== id)
}
</script>

<template>
  <div class="admin-projects">
    <div class="page-header">
      <h1 class="page-title">项目管理</h1>
      <button class="new-btn" @click="openNew">+ 添加项目</button>
    </div>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else class="projects-grid">
      <div v-for="p in projects" :key="p.id" class="project-card">
        <div class="card-header">
          <span class="card-name">{{ p.name }}</span>
          <span class="card-cat">{{ p.category }}</span>
        </div>
        <p class="card-desc">{{ p.description }}</p>
        <div class="card-tags">
          <span v-for="t in p.techStack.slice(0,3)" :key="t" class="tag">{{ t }}</span>
        </div>
        <div class="card-footer">
          <span class="card-status" :class="p.status">{{ p.status === 'active' ? '进行中' : p.status === 'completed' ? '已完成' : '归档' }}</span>
          <div class="card-actions">
            <button class="action-btn" @click="openEdit(p)">编辑</button>
            <button class="action-btn delete" @click="deleteProject(p.id, p.name)">删除</button>
          </div>
        </div>
      </div>
      <div v-if="projects.length === 0" class="empty">还没有项目，添加第一个吧！</div>
    </div>

    <!-- 表单弹窗 -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm=false">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editId ? '编辑项目' : '添加项目' }}</h2>
          <button class="close-btn" @click="showForm=false">×</button>
        </div>
        <div class="modal-body">
          <p v-if="error" class="error-msg">{{ error }}</p>
          <div class="field">
            <label>项目名称 *</label>
            <input v-model="form.name" type="text" placeholder="项目名称" />
          </div>
          <div class="field">
            <label>简介</label>
            <textarea v-model="form.description" rows="2" placeholder="一两句话介绍项目…"></textarea>
          </div>
          <div class="field-row">
            <div class="field">
              <label>分类</label>
              <select v-model="form.category">
                <option>前端</option><option>后端</option><option>全栈</option>
                <option>QT应用</option><option>设计</option><option>工具</option>
              </select>
            </div>
            <div class="field">
              <label>状态</label>
              <select v-model="form.status">
                <option value="active">进行中</option>
                <option value="completed">已完成</option>
                <option value="archived">归档</option>
              </select>
            </div>
          </div>
          <div class="field">
            <label>技术栈（逗号分隔）</label>
            <input v-model="form.techStack" type="text" placeholder="Vue, TypeScript, FastAPI" />
          </div>
          <div class="field-row">
            <div class="field">
              <label>预览链接（「查看」按钮）</label>
              <input v-model="form.link" type="text" placeholder="https://…" />
            </div>
            <div class="field">
              <label>GitHub 链接</label>
              <input v-model="form.githubUrl" type="url" placeholder="https://github.com/…" />
            </div>
          </div>
          <div class="field">
            <label>程序下载链接（「下载程序」按钮）</label>
            <div class="input-with-btn">
              <input v-model="form.downloadUrl" type="text" placeholder="/exes/xxx.zip" />
              <button type="button" class="pick-btn" @click="openExePicker">从程序库选择</button>
            </div>
          </div>
          <div class="field">
            <label>封面图</label>
            <div class="input-with-btn">
              <input v-model="form.cover" type="text" placeholder="/photos/xxx.png" />
              <button type="button" class="pick-btn" @click="showImagePicker = true">从相册选择</button>
            </div>
            <img v-if="form.cover" :src="form.cover" class="cover-preview" />
          </div>
          <div class="field field--check">
            <input id="featured" v-model="form.featured" type="checkbox" />
            <label for="featured">在首页推荐展示</label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showForm=false">取消</button>
          <button class="save-btn" :disabled="saving" @click="saveProject">
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- 封面图选择器 -->
  <ImagePickerModal
    v-if="showImagePicker"
    :current="form.cover"
    @select="(url) => { form.cover = url }"
    @close="showImagePicker = false"
  />

  <!-- exe 选择器 -->
  <div v-if="showExePicker" class="modal-overlay" @click.self="showExePicker = false">
    <div class="modal exe-picker-modal">
      <div class="modal-header">
        <h2>选择程序包</h2>
        <button class="close-btn" @click="showExePicker = false">×</button>
      </div>
      <div class="modal-body">
        <div v-if="!exePickerLoaded" class="exe-empty">加载中…</div>
        <div v-else-if="exeFiles.length === 0" class="exe-empty">
          还没有程序包，请先到「程序管理」页上传。
        </div>
        <div v-else class="exe-list">
          <button
            v-for="f in exeFiles"
            :key="f.filename"
            class="exe-item"
            :class="{ selected: form.downloadUrl === f.url }"
            @click="form.downloadUrl = f.url; showExePicker = false"
          >
            <span class="exe-icon">📦</span>
            <div class="exe-info">
              <span class="exe-name">{{ f.filename }}</span>
              <span class="exe-path">{{ f.url }}</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-projects { width:100%; }
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:2rem; }
.page-title { font-family:'Noto Serif SC',serif; font-size:28px; font-weight:500; color:var(--qi-ink); }
.new-btn { padding:9px 20px; border-radius:999px; background:var(--qi-primary); color:white; font-size:14px; font-weight:500; border:none; cursor:pointer; }
.new-btn:hover { opacity:.88; }
.loading { color:var(--qi-ink-light); }
.projects-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; }
.project-card { background:var(--qi-bg-card); border:1px solid var(--qi-border); border-radius:14px; padding:1.25rem; display:flex; flex-direction:column; gap:.75rem; }
.card-header { display:flex; align-items:center; justify-content:space-between; }
.card-name { font-size:15px; font-weight:600; color:var(--qi-ink); }
.card-cat { font-size:11px; color:var(--qi-primary); background:rgba(255,140,90,.1); padding:2px 8px; border-radius:999px; }
.card-desc { font-size:13px; color:var(--qi-ink-muted); line-height:1.6; flex:1; }
.card-tags { display:flex; flex-wrap:wrap; gap:4px; }
.tag { font-size:11px; padding:2px 8px; border-radius:999px; background:var(--qi-bg); border:1px solid var(--qi-border); color:var(--qi-ink-muted); }
.card-footer { display:flex; align-items:center; justify-content:space-between; }
.card-status { font-size:12px; font-weight:500; }
.card-status.active { color:#4caf50; }
.card-status.completed { color:var(--qi-primary); }
.card-status.archived { color:var(--qi-ink-light); }
.card-actions { display:flex; gap:.5rem; }
.action-btn { font-size:12px; padding:4px 10px; border-radius:6px; border:1px solid var(--qi-border); background:transparent; color:var(--qi-ink-muted); cursor:pointer; }
.action-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); }
.action-btn.delete { color:#e05050; border-color:transparent; }
.action-btn.delete:hover { background:rgba(224,80,80,.08); }
.empty { grid-column:1/-1; text-align:center; padding:3rem; font-size:14px; color:var(--qi-ink-light); }
/* modal */
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; z-index:1000; }
.modal { width:560px; max-width:95vw; max-height:90vh; overflow-y:auto; background:var(--qi-bg-card); border-radius:18px; box-shadow:0 16px 48px rgba(0,0,0,.2); }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding:1.25rem 1.5rem; border-bottom:1px solid var(--qi-border); }
.modal-header h2 { font-family:'Noto Serif SC',serif; font-size:18px; font-weight:500; color:var(--qi-ink); }
.close-btn { font-size:22px; line-height:1; background:none; border:none; color:var(--qi-ink-light); cursor:pointer; }
.modal-body { padding:1.5rem; display:flex; flex-direction:column; gap:1rem; }
.field { display:flex; flex-direction:column; gap:.35rem; }
.field-row { display:grid; grid-template-columns:1fr 1fr; gap:.75rem; }
.field--check { flex-direction:row; align-items:center; gap:.5rem; }
.field--check input { width:auto; }
.field label { font-size:13px; font-weight:500; color:var(--qi-ink-muted); }
.field input,.field textarea,.field select { padding:8px 12px; border-radius:8px; border:1.5px solid var(--qi-border); background:var(--qi-bg); font-size:13.5px; color:var(--qi-ink); outline:none; font-family:inherit; }
.field input:focus,.field textarea:focus,.field select:focus { border-color:var(--qi-primary); }
.modal-footer { display:flex; justify-content:flex-end; gap:.75rem; padding:1.25rem 1.5rem; border-top:1px solid var(--qi-border); }
.cancel-btn { padding:8px 18px; border-radius:999px; border:1.5px solid var(--qi-border); background:transparent; color:var(--qi-ink-muted); font-size:14px; cursor:pointer; }
.save-btn { padding:8px 22px; border-radius:999px; background:var(--qi-primary); color:white; font-size:14px; font-weight:500; border:none; cursor:pointer; }
.save-btn:disabled { opacity:.6; cursor:not-allowed; }
.error-msg { font-size:13px; color:#e05050; background:rgba(224,80,80,.06); border:1px solid rgba(224,80,80,.2); border-radius:8px; padding:.75rem 1rem; }
.cover-preview { margin-top:.4rem; width:100%; max-height:120px; object-fit:cover; border-radius:8px; border:1px solid var(--qi-border); }
.input-with-btn { display:flex; gap:.5rem; }
.input-with-btn input { flex:1; min-width:0; }
.pick-btn {
  flex-shrink:0; padding:7px 12px; border-radius:8px; font-size:12.5px; font-weight:500;
  border:1.5px solid var(--qi-border); background:var(--qi-bg); color:var(--qi-ink-muted);
  cursor:pointer; white-space:nowrap; transition:all .15s;
}
.pick-btn:hover { border-color:var(--qi-primary); color:var(--qi-primary); }
.exe-picker-modal { width:480px; }
.exe-empty { padding:2rem; text-align:center; color:var(--qi-ink-light); font-size:13.5px; }
.exe-list { display:flex; flex-direction:column; gap:.4rem; }
.exe-item {
  all:unset; display:flex; align-items:center; gap:.75rem; padding:.7rem .9rem;
  border-radius:10px; border:1.5px solid var(--qi-border); cursor:pointer; transition:all .15s;
}
.exe-item:hover, .exe-item.selected { border-color:var(--qi-primary); background:rgba(255,140,90,.05); }
.exe-icon { font-size:18px; flex-shrink:0; }
.exe-info { display:flex; flex-direction:column; gap:.1rem; min-width:0; }
.exe-name { font-size:13.5px; font-weight:500; color:var(--qi-ink); }
.exe-path { font-size:11.5px; color:var(--qi-ink-light); font-family:monospace; }
@media(max-width:600px){.projects-grid{grid-template-columns:1fr;}.field-row{grid-template-columns:1fr;}}
</style>
