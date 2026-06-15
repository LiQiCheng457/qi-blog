<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { exesApi } from '@/api/exes'
import type { ExeFile } from '@/api/exes'

const files    = ref<ExeFile[]>([])
const loading  = ref(true)
const uploading = ref(false)
const uploadErr = ref('')
const copied   = ref('')
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement>()

async function load() {
  loading.value = true
  try { files.value = await exesApi.list() }
  finally { loading.value = false }
}
onMounted(load)

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

async function uploadFiles(fileList: FileList | null) {
  if (!fileList?.length) return
  uploadErr.value = ''
  uploading.value = true
  try {
    for (const f of Array.from(fileList)) {
      const result = await exesApi.upload(f)
      files.value.unshift(result)
    }
    if (fileInput.value) fileInput.value.value = ''
  } catch (e: any) {
    uploadErr.value = e.message ?? '上传失败'
  } finally {
    uploading.value = false
  }
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  uploadFiles(e.dataTransfer?.files ?? null)
}

function onFileChange(e: Event) {
  uploadFiles((e.target as HTMLInputElement).files)
}

async function copyPath(url: string) {
  await navigator.clipboard.writeText(url)
  copied.value = url
  setTimeout(() => { copied.value = '' }, 1800)
}

async function deleteFile(f: ExeFile) {
  if (!confirm(`确定删除「${f.filename}」？`)) return
  await exesApi.delete(f.filename)
  files.value = files.value.filter(x => x.filename !== f.filename)
}
</script>

<template>
  <div class="admin-exes">
    <div class="page-header">
      <h1 class="page-title">程序管理</h1>
      <p class="page-sub">管理可供下载的程序包，复制路径后填入项目的「下载链接」字段。</p>
    </div>

    <!-- 上传区 -->
    <div
      class="upload-zone"
      :class="{ 'drag-over': dragOver }"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()"
    >
      <input ref="fileInput" type="file" accept=".zip,.exe,.7z,.rar" multiple hidden @change="onFileChange" />
      <div v-if="uploading" class="upload-hint">上传中…</div>
      <div v-else class="upload-hint">
        <span class="upload-icon">📦</span>
        点击或拖入程序包（.zip / .exe / .7z / .rar，最大 300 MB）
      </div>
    </div>
    <p v-if="uploadErr" class="upload-err">{{ uploadErr }}</p>

    <!-- 文件列表 -->
    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="files.length === 0" class="empty">还没有程序包，上传第一个吧！</div>
    <div v-else class="file-list">
      <div v-for="f in files" :key="f.filename" class="file-row">
        <span class="file-icon">📦</span>
        <div class="file-info">
          <span class="file-name">{{ f.filename }}</span>
          <span class="file-size">{{ formatSize(f.size) }}</span>
        </div>
        <code class="file-url">{{ f.url }}</code>
        <div class="file-actions">
          <button
            class="action-btn copy"
            :class="{ copied: copied === f.url }"
            @click="copyPath(f.url)"
          >
            {{ copied === f.url ? '已复制 ✓' : '复制路径' }}
          </button>
          <button class="action-btn delete" @click="deleteFile(f)">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-exes { width: 100%; }
.page-header { margin-bottom: 1.75rem; }
.page-title { font-family:'Noto Serif SC',serif; font-size:28px; font-weight:500; color:var(--qi-ink); margin-bottom:.35rem; }
.page-sub { font-size:13.5px; color:var(--qi-ink-muted); }

.upload-zone {
  border: 2px dashed var(--qi-border); border-radius: 14px;
  padding: 2.5rem 1.5rem; text-align: center; cursor: pointer;
  transition: border-color .2s, background .2s; margin-bottom: 1rem;
  background: var(--qi-bg);
}
.upload-zone:hover, .upload-zone.drag-over {
  border-color: var(--qi-primary); background: rgba(255,140,90,.04);
}
.upload-icon { font-size: 28px; display: block; margin-bottom: .5rem; }
.upload-hint { font-size: 13.5px; color: var(--qi-ink-muted); line-height: 1.6; }
.upload-err { font-size: 13px; color: #e05050; margin-bottom: 1rem; }

.empty { text-align:center; padding:3rem; font-size:14px; color:var(--qi-ink-light); }

.file-list { display:flex; flex-direction:column; gap:.5rem; }
.file-row {
  display: flex; align-items: center; gap: 1rem;
  background: var(--qi-bg-card); border: 1px solid var(--qi-border);
  border-radius: 12px; padding: .9rem 1.1rem;
}
.file-icon { font-size: 20px; flex-shrink: 0; }
.file-info { display:flex; flex-direction:column; gap:.1rem; min-width:0; flex:1; }
.file-name { font-size:14px; font-weight:500; color:var(--qi-ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.file-size { font-size:12px; color:var(--qi-ink-light); }
.file-url {
  font-size: 12px; color: var(--qi-ink-muted); background: var(--qi-bg);
  border: 1px solid var(--qi-border); border-radius: 6px; padding: 3px 8px;
  white-space: nowrap; flex-shrink: 0; max-width: 200px; overflow:hidden; text-overflow:ellipsis;
}
.file-actions { display:flex; gap:.5rem; flex-shrink:0; }
.action-btn {
  font-size:12px; padding:5px 12px; border-radius:6px;
  border:1px solid var(--qi-border); background:transparent;
  color:var(--qi-ink-muted); cursor:pointer; white-space:nowrap; transition:all .15s;
}
.action-btn.copy:hover, .action-btn.copy.copied {
  border-color: var(--qi-primary); color: var(--qi-primary);
}
.action-btn.delete { color:#e05050; border-color:transparent; }
.action-btn.delete:hover { background:rgba(224,80,80,.08); }

@media(max-width:640px){
  .file-row { flex-wrap:wrap; }
  .file-url { max-width: 100%; }
}
</style>
