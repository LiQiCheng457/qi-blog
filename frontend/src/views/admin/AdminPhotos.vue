<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { photosApi } from '@/api/photos'
import type { Photo } from '@/types'

const photos   = ref<Photo[]>([])
const loading  = ref(true)
const uploading = ref(false)
const uploadErr = ref('')

// ── 上传表单 ──────────────────────────────────────────────────────
const dragOver  = ref(false)
const fileInput = ref<HTMLInputElement>()
const pendingFiles = ref<File[]>([])
const uploadAlt = ref('')
const uploadTag = ref('')

const KNOWN_TAGS = ['水豚祁', '日常', '搞笑', '电影', 'QT应用']
const existingTags = computed(() => {
  const set = new Set(photos.value.map(p => p.tag).filter(Boolean))
  return [...new Set([...KNOWN_TAGS, ...set])]
})

// ── 编辑弹窗 ──────────────────────────────────────────────────────
const editPhoto = ref<Photo | null>(null)
const editAlt   = ref('')
const editTag   = ref('')
const editSaving = ref(false)

// ── 过滤 ──────────────────────────────────────────────────────────
const filterTag = ref('全部')
const filtered  = computed(() =>
  filterTag.value === '全部' ? photos.value : photos.value.filter(p => p.tag === filterTag.value)
)
const allTags   = computed(() => ['全部', ...existingTags.value])

async function load() {
  loading.value = true
  try { photos.value = await photosApi.list() }
  finally { loading.value = false }
}
onMounted(load)

// ── 文件选择 ──────────────────────────────────────────────────────
function onDrop(e: DragEvent) {
  dragOver.value = false
  const files = [...(e.dataTransfer?.files ?? [])]
  pendingFiles.value = files.filter(f => f.type.startsWith('image/'))
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  pendingFiles.value = [...(input.files ?? [])]
}

function removePending(i: number) {
  pendingFiles.value.splice(i, 1)
}

// ── 批量上传 ──────────────────────────────────────────────────────
async function doUpload() {
  if (!pendingFiles.value.length) return
  uploadErr.value = ''
  uploading.value = true
  try {
    for (const file of pendingFiles.value) {
      const alt = uploadAlt.value.trim() || file.name.replace(/\.[^.]+$/, '')
      const photo = await photosApi.upload(file, alt, uploadTag.value.trim())
      photos.value.unshift(photo)
    }
    pendingFiles.value = []
    uploadAlt.value = ''
    uploadTag.value = ''
    if (fileInput.value) fileInput.value.value = ''
  } catch (e: any) {
    uploadErr.value = e.message ?? '上传失败'
  } finally {
    uploading.value = false
  }
}

// ── 编辑 ──────────────────────────────────────────────────────────
function openEdit(photo: Photo) {
  editPhoto.value = photo
  editAlt.value   = photo.alt
  editTag.value   = photo.tag
}

async function saveEdit() {
  if (!editPhoto.value) return
  editSaving.value = true
  try {
    const updated = await photosApi.update(editPhoto.value.id, {
      alt: editAlt.value,
      tag: editTag.value,
    })
    const idx = photos.value.findIndex(p => p.id === updated.id)
    if (idx !== -1) photos.value[idx] = updated
    editPhoto.value = null
  } finally {
    editSaving.value = false
  }
}

// ── 删除 ──────────────────────────────────────────────────────────
function objectUrl(file: File) {
  return URL.createObjectURL(file)
}

async function deletePhoto(photo: Photo) {
  if (!confirm(`确定删除「${photo.alt || photo.url}」？文件也会同步删除。`)) return
  await photosApi.delete(photo.id)
  photos.value = photos.value.filter(p => p.id !== photo.id)
}
</script>

<template>
  <div class="admin-photos">
    <div class="page-header">
      <h1 class="page-title">图片管理</h1>
      <span class="photo-count">共 {{ photos.length }} 张</span>
    </div>

    <!-- 上传区域 -->
    <div class="upload-section">
      <div
        class="drop-zone"
        :class="{ 'drop-zone--over': dragOver }"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          multiple
          class="file-input"
          @change="onFileChange"
        />
        <div class="drop-content">
          <span class="drop-icon">🖼</span>
          <p class="drop-hint">拖拽图片到这里，或点击选择文件</p>
          <p class="drop-sub">支持 JPG / PNG / WebP / GIF，单文件最大 10 MB</p>
        </div>
      </div>

      <!-- 待上传列表 -->
      <div v-if="pendingFiles.length" class="pending-list">
        <div v-for="(f, i) in pendingFiles" :key="i" class="pending-item">
          <img :src="objectUrl(f)" class="pending-thumb" />
          <span class="pending-name">{{ f.name }}</span>
          <button class="remove-btn" @click="removePending(i)">×</button>
        </div>

        <div class="upload-meta">
          <div class="meta-field">
            <label>描述（Alt）</label>
            <input
              v-model="uploadAlt"
              type="text"
              placeholder="多张图片时留空则用文件名"
            />
          </div>
          <div class="meta-field">
            <label>标签</label>
            <input
              v-model="uploadTag"
              type="text"
              list="tag-list"
              placeholder="选择或输入标签"
            />
            <datalist id="tag-list">
              <option v-for="t in existingTags" :key="t" :value="t" />
            </datalist>
          </div>
        </div>

        <p v-if="uploadErr" class="upload-err">{{ uploadErr }}</p>

        <div class="upload-actions">
          <button class="cancel-btn" @click="pendingFiles = []">取消</button>
          <button class="upload-btn" :disabled="uploading" @click="doUpload">
            {{ uploading ? `上传中 (${pendingFiles.length} 张)…` : `上传 ${pendingFiles.length} 张` }}
          </button>
        </div>
      </div>
    </div>

    <!-- 过滤标签 -->
    <div class="filter-bar">
      <button
        v-for="t in allTags"
        :key="t"
        class="filter-tab"
        :class="{ active: filterTag === t }"
        @click="filterTag = t"
      >{{ t }}</button>
    </div>

    <!-- 图片网格 -->
    <div v-if="loading" class="state-msg">加载中…</div>
    <div v-else-if="filtered.length === 0" class="state-msg">没有图片</div>
    <div v-else class="photo-grid">
      <div v-for="photo in filtered" :key="photo.id" class="photo-card">
        <div class="photo-thumb-wrap">
          <img :src="photo.url" :alt="photo.alt" class="photo-thumb" loading="lazy" />
          <div class="photo-actions">
            <button class="pa-btn" @click="openEdit(photo)">编辑</button>
            <button class="pa-btn pa-btn--del" @click="deletePhoto(photo)">删除</button>
          </div>
        </div>
        <div class="photo-meta">
          <span class="photo-tag">{{ photo.tag || '—' }}</span>
          <span class="photo-alt">{{ photo.alt || '（无描述）' }}</span>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div v-if="editPhoto" class="modal-overlay" @click.self="editPhoto = null">
      <div class="modal">
        <div class="modal-header">
          <h2>编辑图片信息</h2>
          <button class="close-btn" @click="editPhoto = null">×</button>
        </div>
        <div class="modal-body">
          <img :src="editPhoto.url" :alt="editPhoto.alt" class="edit-preview" />
          <div class="field">
            <label>描述（Alt）</label>
            <input v-model="editAlt" type="text" placeholder="图片描述…" />
          </div>
          <div class="field">
            <label>标签</label>
            <input v-model="editTag" type="text" list="tag-list-edit" placeholder="标签" />
            <datalist id="tag-list-edit">
              <option v-for="t in existingTags" :key="t" :value="t" />
            </datalist>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="editPhoto = null">取消</button>
          <button class="save-btn" :disabled="editSaving" @click="saveEdit">
            {{ editSaving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-photos { width: 100%; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
.page-title { font-family: 'Noto Serif SC', serif; font-size: 28px; font-weight: 500; color: var(--qi-ink); }
.photo-count { font-size: 13px; color: var(--qi-ink-light); }

/* 上传区 */
.upload-section { margin-bottom: 2rem; }
.drop-zone {
  border: 2px dashed var(--qi-border);
  border-radius: 14px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: border-color .2s, background .2s;
  position: relative;
}
.drop-zone:hover, .drop-zone--over {
  border-color: var(--qi-primary);
  background: rgba(255, 140, 90, .04);
}
.file-input { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
.drop-content { pointer-events: none; }
.drop-icon { font-size: 32px; display: block; margin-bottom: .5rem; }
.drop-hint { font-size: 15px; color: var(--qi-ink); margin-bottom: .25rem; }
.drop-sub { font-size: 12px; color: var(--qi-ink-light); }

/* 待上传列表 */
.pending-list { margin-top: 1rem; background: var(--qi-bg-card); border: 1px solid var(--qi-border); border-radius: 12px; padding: 1rem; display: flex; flex-direction: column; gap: .75rem; }
.pending-item { display: flex; align-items: center; gap: .75rem; }
.pending-thumb { width: 52px; height: 52px; object-fit: cover; border-radius: 6px; flex-shrink: 0; border: 1px solid var(--qi-border); }
.pending-name { flex: 1; font-size: 13px; color: var(--qi-ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.remove-btn { font-size: 18px; line-height: 1; background: none; border: none; color: var(--qi-ink-light); cursor: pointer; padding: 0 4px; flex-shrink: 0; }
.remove-btn:hover { color: #e05050; }

.upload-meta { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; padding-top: .25rem; }
.meta-field { display: flex; flex-direction: column; gap: .3rem; }
.meta-field label { font-size: 12px; font-weight: 500; color: var(--qi-ink-muted); }
.meta-field input { padding: 7px 10px; border-radius: 8px; border: 1.5px solid var(--qi-border); background: var(--qi-bg); font-size: 13px; color: var(--qi-ink); outline: none; }
.meta-field input:focus { border-color: var(--qi-primary); }

.upload-err { font-size: 13px; color: #e05050; }
.upload-actions { display: flex; justify-content: flex-end; gap: .5rem; }
.upload-btn { padding: 8px 22px; border-radius: 999px; background: var(--qi-primary); color: white; font-size: 14px; font-weight: 500; border: none; cursor: pointer; }
.upload-btn:disabled { opacity: .6; cursor: not-allowed; }

/* 过滤标签 */
.filter-bar { display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: 1.25rem; }
.filter-tab { font-size: 12.5px; padding: 5px 14px; border-radius: 999px; border: 1.5px solid var(--qi-border); background: transparent; color: var(--qi-ink-muted); cursor: pointer; transition: all .15s; }
.filter-tab:hover, .filter-tab.active { background: var(--qi-primary); border-color: var(--qi-primary); color: white; }

/* 图片网格 */
.photo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: .75rem; }
.photo-card { border-radius: 10px; overflow: hidden; border: 1px solid var(--qi-border); background: var(--qi-bg-card); }
.photo-thumb-wrap { position: relative; aspect-ratio: 4/3; overflow: hidden; background: var(--qi-bg-muted); }
.photo-thumb { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .3s; }
.photo-card:hover .photo-thumb { transform: scale(1.04); }
.photo-actions {
  position: absolute; inset: 0;
  background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; gap: .5rem;
  opacity: 0; transition: opacity .2s;
}
.photo-card:hover .photo-actions { opacity: 1; }
.pa-btn { font-size: 12px; padding: 5px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,.4); background: rgba(255,255,255,.15); color: white; cursor: pointer; backdrop-filter: blur(4px); transition: background .15s; }
.pa-btn:hover { background: rgba(255,255,255,.3); }
.pa-btn--del:hover { background: rgba(224,80,80,.7); border-color: transparent; }
.photo-meta { padding: .5rem .6rem; }
.photo-tag { display: inline-block; font-size: 10.5px; font-weight: 600; padding: 2px 8px; border-radius: 999px; background: rgba(255,140,90,.1); color: var(--qi-primary); margin-bottom: .3rem; }
.photo-alt { display: block; font-size: 12px; color: var(--qi-ink-muted); line-height: 1.5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.state-msg { text-align: center; padding: 3rem; font-size: 14px; color: var(--qi-ink-light); }
.cancel-btn { padding: 8px 18px; border-radius: 999px; border: 1.5px solid var(--qi-border); background: transparent; color: var(--qi-ink-muted); font-size: 14px; cursor: pointer; }

/* 弹窗 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { width: 460px; max-width: 95vw; background: var(--qi-bg-card); border-radius: 18px; box-shadow: 0 16px 48px rgba(0,0,0,.2); overflow: hidden; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--qi-border); }
.modal-header h2 { font-family: 'Noto Serif SC', serif; font-size: 18px; font-weight: 500; color: var(--qi-ink); }
.close-btn { font-size: 22px; background: none; border: none; color: var(--qi-ink-light); cursor: pointer; }
.modal-body { padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
.edit-preview { width: 100%; max-height: 220px; object-fit: contain; border-radius: 8px; background: var(--qi-bg-muted); }
.field { display: flex; flex-direction: column; gap: .35rem; }
.field label { font-size: 13px; font-weight: 500; color: var(--qi-ink-muted); }
.field input { padding: 8px 12px; border-radius: 8px; border: 1.5px solid var(--qi-border); background: var(--qi-bg); font-size: 13.5px; color: var(--qi-ink); outline: none; }
.field input:focus { border-color: var(--qi-primary); }
.modal-footer { display: flex; justify-content: flex-end; gap: .75rem; padding: 1.25rem 1.5rem; border-top: 1px solid var(--qi-border); }
.save-btn { padding: 8px 22px; border-radius: 999px; background: var(--qi-primary); color: white; font-size: 14px; font-weight: 500; border: none; cursor: pointer; }
.save-btn:disabled { opacity: .6; cursor: not-allowed; }

@media (max-width: 600px) {
  .upload-meta { grid-template-columns: 1fr; }
  .photo-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
