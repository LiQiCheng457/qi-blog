<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{ modelValue: string }>()
const emit  = defineEmits<{ 'update:modelValue': [v: string] }>()

const mode = ref<'split' | 'edit' | 'preview'>('split')
const ta   = ref<HTMLTextAreaElement | null>(null)

const rendered = computed(() => marked(props.modelValue ?? '', { breaks: true }))

function onInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLTextAreaElement).value)
}

function insertAt(before: string, after = '') {
  const el = ta.value
  if (!el) return
  const start = el.selectionStart
  const end   = el.selectionEnd
  const sel   = el.value.slice(start, end)
  const newVal = el.value.slice(0, start) + before + sel + after + el.value.slice(end)
  emit('update:modelValue', newVal)
  // restore cursor
  setTimeout(() => {
    el.focus()
    el.setSelectionRange(start + before.length, start + before.length + sel.length)
  })
}

const toolbar = [
  { label: 'B', title: '加粗', fn: () => insertAt('**', '**') },
  { label: 'I', title: '斜体', fn: () => insertAt('*', '*') },
  { label: 'H2', title: '标题', fn: () => insertAt('\n## ') },
  { label: '```', title: '代码块', fn: () => insertAt('\n```\n', '\n```\n') },
  { label: '链接', title: '插入链接', fn: () => insertAt('[', '](url)') },
  { label: '引用', title: '引用', fn: () => insertAt('\n> ') },
]
</script>

<template>
  <div class="md-editor">
    <div class="md-toolbar">
      <button v-for="btn in toolbar" :key="btn.label" class="tb-btn" :title="btn.title" type="button"
        @click="btn.fn()">{{ btn.label }}</button>
      <div class="tb-sep"></div>
      <button class="tb-btn" :class="{active:mode==='edit'}"    type="button" @click="mode='edit'">编辑</button>
      <button class="tb-btn" :class="{active:mode==='split'}"   type="button" @click="mode='split'">分栏</button>
      <button class="tb-btn" :class="{active:mode==='preview'}" type="button" @click="mode='preview'">预览</button>
    </div>

    <div class="md-body" :class="mode">
      <textarea v-if="mode !== 'preview'" ref="ta"
        class="md-textarea" :value="modelValue" @input="onInput"
        placeholder="用 Markdown 写点什么……" spellcheck="false"></textarea>
      <div v-if="mode !== 'edit'"
        class="md-preview" v-html="rendered"></div>
    </div>
  </div>
</template>

<style scoped>
.md-editor { display:flex; flex-direction:column; border:1.5px solid var(--qi-border); border-radius:12px; overflow:hidden; background:var(--qi-bg-card); }
.md-toolbar { display:flex; align-items:center; gap:2px; padding:.5rem .75rem; border-bottom:1px solid var(--qi-border); background:var(--qi-bg); flex-wrap:wrap; }
.tb-btn { padding:4px 10px; border-radius:6px; border:none; background:transparent; font-size:12px; font-weight:500; color:var(--qi-ink-muted); cursor:pointer; transition:all .15s; }
.tb-btn:hover,.tb-btn.active { background:rgba(255,140,90,.12); color:var(--qi-primary); }
.tb-sep { flex:1; }
.md-body { display:flex; min-height:400px; }
.md-body.edit .md-textarea { width:100%; }
.md-body.preview .md-preview { width:100%; }
.md-body.split .md-textarea { width:50%; border-right:1px solid var(--qi-border); }
.md-body.split .md-preview { width:50%; }
.md-textarea { flex:1; border:none; outline:none; resize:none; padding:1.25rem; font-family:'JetBrains Mono','Fira Code',monospace; font-size:13.5px; line-height:1.7; color:var(--qi-ink); background:transparent; }
.md-preview { flex:1; padding:1.25rem 1.5rem; overflow-y:auto; line-height:1.9; color:var(--qi-ink); font-size:14px; }
.md-preview :deep(h1),.md-preview :deep(h2),.md-preview :deep(h3) { font-family:'Noto Serif SC',serif; font-weight:500; margin:1.5rem 0 .75rem; color:var(--qi-ink); }
.md-preview :deep(h2){font-size:20px;} .md-preview :deep(h3){font-size:16px;}
.md-preview :deep(p) { margin-bottom:1rem; color:var(--qi-ink-muted); }
.md-preview :deep(code) { font-family:'JetBrains Mono',monospace; font-size:13px; }
.md-preview :deep(pre) { background:var(--qi-bg); border:1px solid var(--qi-border); border-radius:8px; padding:1rem; overflow-x:auto; margin:1rem 0; }
.md-preview :deep(:not(pre)>code) { background:rgba(255,140,90,.1); color:var(--qi-primary); padding:1px 5px; border-radius:4px; }
.md-preview :deep(blockquote) { border-left:3px solid var(--qi-primary); padding-left:1rem; color:var(--qi-ink-muted); font-style:italic; margin:1rem 0; }
.md-preview :deep(ul),.md-preview :deep(ol) { padding-left:1.5rem; margin-bottom:1rem; }
.md-preview :deep(li) { margin-bottom:.25rem; color:var(--qi-ink-muted); }
.md-preview :deep(a) { color:var(--qi-primary); }
</style>
