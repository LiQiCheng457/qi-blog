<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

type ModeKey = 'work' | 'short' | 'long'

interface DurationConfig {
  work: number   // minutes
  short: number
  long: number
}

const DURATION_KEY   = 'qi-pomodoro-durations'
const DEFAULT_DURATIONS: DurationConfig = { work: 25, short: 5, long: 15 }

const durations = ref<DurationConfig>({ ...DEFAULT_DURATIONS })

const MODES = computed(() => [
  { key: 'work'  as ModeKey, label: '番茄', duration: durations.value.work  * 60 },
  { key: 'short' as ModeKey, label: '短休', duration: durations.value.short * 60 },
  { key: 'long'  as ModeKey, label: '长休', duration: durations.value.long  * 60 },
])

// 按天存 localStorage
const TODAY_KEY = `qi-pomodoro-${new Date().toISOString().slice(0, 10)}`

const mode      = ref<ModeKey>('work')
const timeLeft  = ref(DEFAULT_DURATIONS.work * 60)
const isRunning = ref(false)
const completedToday = ref(0)

// ── 设置面板 ──────────────────────────────────────────────────────────
const showSettings = ref(false)
const editWork  = ref(DEFAULT_DURATIONS.work)
const editShort = ref(DEFAULT_DURATIONS.short)
const editLong  = ref(DEFAULT_DURATIONS.long)

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, Math.round(n)))
}

function openSettings() {
  editWork.value  = durations.value.work
  editShort.value = durations.value.short
  editLong.value  = durations.value.long
  showSettings.value = true
}

function cancelSettings() {
  showSettings.value = false
}

function saveSettings() {
  durations.value = {
    work:  clamp(editWork.value,  1, 180),
    short: clamp(editShort.value, 1, 60),
    long:  clamp(editLong.value,  1, 120),
  }
  localStorage.setItem(DURATION_KEY, JSON.stringify(durations.value))
  // 若当前计时器未运行，立即重置剩余时间
  if (!isRunning.value) {
    timeLeft.value = currentModeDuration.value
  }
  showSettings.value = false
}

function resetToDefault() {
  editWork.value  = DEFAULT_DURATIONS.work
  editShort.value = DEFAULT_DURATIONS.short
  editLong.value  = DEFAULT_DURATIONS.long
}

let interval: ReturnType<typeof setInterval> | null = null
let audioCtx: AudioContext | null = null

// ── 进度环 ────────────────────────────────────────────────────────────
const RADIUS = 76
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

const currentModeDuration = computed(
  () => MODES.value.find(m => m.key === mode.value)!.duration
)
const dashOffset = computed(() => CIRCUMFERENCE * (timeLeft.value / currentModeDuration.value))

const timeDisplay = computed(() => {
  const m = Math.floor(timeLeft.value / 60)
  const s = timeLeft.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const statusLabel = computed(() => {
  if (timeLeft.value === currentModeDuration.value && !isRunning.value) return ''
  if (isRunning.value) return mode.value === 'work' ? '专注中' : '休息中'
  return '已暂停'
})

// ── 今日计数 ──────────────────────────────────────────────────────────
function loadCompleted(): number {
  return parseInt(localStorage.getItem(TODAY_KEY) ?? '0', 10) || 0
}
function saveCompleted() {
  localStorage.setItem(TODAY_KEY, String(completedToday.value))
}

const cycleProgress = computed(() => completedToday.value % 4)

// ── 音效 ──────────────────────────────────────────────────────────────
function ensureAudioCtx() {
  if (!audioCtx) audioCtx = new AudioContext()
  if (audioCtx.state === 'suspended') audioCtx.resume()
  return audioCtx
}

function playBeep() {
  try {
    const ctx = ensureAudioCtx()
    const osc  = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.type = 'sine'
    osc.frequency.value = mode.value === 'work' ? 660 : 440
    gain.gain.setValueAtTime(0.35, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2)
    osc.start()
    osc.stop(ctx.currentTime + 1.2)
  } catch {}
}

// ── 计时器控制 ────────────────────────────────────────────────────────
function setMode(key: ModeKey) {
  mode.value     = key
  timeLeft.value = MODES.value.find(m => m.key === key)!.duration
}

function pause() {
  isRunning.value = false
  if (interval) { clearInterval(interval); interval = null }
}

function start() {
  if (isRunning.value) return
  ensureAudioCtx()
  isRunning.value = true
  interval = setInterval(() => {
    if (timeLeft.value <= 0) {
      clearInterval(interval!); interval = null
      isRunning.value = false
      onComplete()
      return
    }
    timeLeft.value--
  }, 1000)
}

function reset() {
  pause()
  timeLeft.value = currentModeDuration.value
}

function switchMode(key: ModeKey) {
  pause()
  setMode(key)
}

function onComplete() {
  playBeep()
  if (mode.value === 'work') {
    completedToday.value++
    saveCompleted()
    setMode(completedToday.value % 4 === 0 ? 'long' : 'short')
  } else {
    setMode('work')
  }
}

onMounted(() => {
  completedToday.value = loadCompleted()
  try {
    const saved = JSON.parse(localStorage.getItem(DURATION_KEY) ?? 'null')
    if (saved && typeof saved.work === 'number') {
      durations.value = {
        work:  clamp(saved.work,  1, 180),
        short: clamp(saved.short, 1, 60),
        long:  clamp(saved.long,  1, 120),
      }
      timeLeft.value = durations.value.work * 60
    }
  } catch {}
})
onUnmounted(() => {
  if (interval) clearInterval(interval)
  audioCtx?.close()
})
</script>

<template>
  <div class="pomodoro-widget">
    <!-- 模式切换 + 设置按钮 -->
    <div class="top-row">
      <div class="mode-tabs">
        <button
          v-for="m in MODES"
          :key="m.key"
          class="mode-tab"
          :class="{ active: mode === m.key }"
          @click="switchMode(m.key)"
        >{{ m.label }}</button>
      </div>
      <button
        class="settings-btn"
        :class="{ active: showSettings }"
        @click="showSettings ? cancelSettings() : openSettings()"
        aria-label="自定义时长"
        title="自定义时长"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>
    </div>

    <!-- 自定义时长面板 -->
    <Transition name="settings-slide">
      <div v-if="showSettings" class="settings-panel">
        <div class="settings-row">
          <span class="settings-label">番茄时长</span>
          <div class="settings-input-wrap">
            <input
              v-model.number="editWork"
              type="number" min="1" max="180"
              class="settings-input"
              @change="editWork = clamp(editWork, 1, 180)"
            />
            <span class="settings-unit">分钟</span>
          </div>
        </div>
        <div class="settings-row">
          <span class="settings-label">短休时长</span>
          <div class="settings-input-wrap">
            <input
              v-model.number="editShort"
              type="number" min="1" max="60"
              class="settings-input"
              @change="editShort = clamp(editShort, 1, 60)"
            />
            <span class="settings-unit">分钟</span>
          </div>
        </div>
        <div class="settings-row">
          <span class="settings-label">长休时长</span>
          <div class="settings-input-wrap">
            <input
              v-model.number="editLong"
              type="number" min="1" max="120"
              class="settings-input"
              @change="editLong = clamp(editLong, 1, 120)"
            />
            <span class="settings-unit">分钟</span>
          </div>
        </div>
        <div class="settings-footer">
          <button class="settings-reset" @click="resetToDefault">恢复默认</button>
          <div class="settings-actions">
            <button class="settings-cancel" @click="cancelSettings">取消</button>
            <button class="settings-save" @click="saveSettings">保存</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 进度环 -->
    <div class="ring-wrap">
      <svg viewBox="0 0 200 200" class="ring-svg" aria-hidden="true">
        <circle cx="100" cy="100" :r="RADIUS" class="ring-track" />
        <circle
          cx="100" cy="100" :r="RADIUS"
          class="ring-progress"
          :class="mode"
          :stroke-dasharray="CIRCUMFERENCE"
          :stroke-dashoffset="dashOffset"
        />
      </svg>

      <div class="ring-center">
        <span class="time-display" :aria-label="`剩余时间 ${timeDisplay}`">{{ timeDisplay }}</span>
        <span v-if="statusLabel" class="status-label">{{ statusLabel }}</span>
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="controls">
      <button class="ctrl-btn reset-btn" @click="reset" aria-label="重置">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
          <path d="M3 3v5h5"/>
        </svg>
        重置
      </button>
      <button class="ctrl-btn start-btn" :class="mode" @click="isRunning ? pause() : start()">
        {{ isRunning ? '暂停' : '开始' }}
      </button>
    </div>

    <!-- 今日进度 -->
    <div class="today-row">
      <span class="today-label">今日番茄</span>
      <div class="cycle-dots" aria-label="本组进度">
        <span
          v-for="i in 4"
          :key="i"
          class="dot"
          :class="{ filled: i <= cycleProgress }"
        />
      </div>
      <span class="today-count">{{ completedToday }} 个</span>
    </div>
  </div>
</template>

<style scoped>
.pomodoro-widget {
  width: 100%;
  padding: 1rem 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.125rem;
}

/* 顶部行：模式标签 + 设置按钮 */
.top-row {
  display: flex;
  align-items: center;
  gap: .5rem;
  width: 100%;
}
.mode-tabs {
  display: flex;
  gap: .25rem;
  background: var(--qi-bg-muted);
  border-radius: 10px;
  padding: 3px;
  flex: 1;
}
.mode-tab {
  flex: 1;
  padding: .375rem .5rem;
  border-radius: 7px;
  border: none;
  background: none;
  color: var(--qi-ink-muted);
  font-size: .82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all .2s;
}
.mode-tab.active {
  background: var(--qi-bg-card);
  color: var(--qi-ink);
  box-shadow: 0 1px 4px var(--qi-shadow);
}

.settings-btn {
  flex-shrink: 0;
  width: 30px; height: 30px;
  border-radius: 8px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-muted);
  color: var(--qi-ink-muted);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s;
}
.settings-btn:hover,
.settings-btn.active {
  border-color: var(--qi-primary);
  color: var(--qi-primary);
  background: rgba(255, 140, 90, 0.08);
}

/* 设置面板 */
.settings-panel {
  width: 100%;
  background: var(--qi-bg-muted);
  border: 1.5px solid var(--qi-border);
  border-radius: 12px;
  padding: .875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: .625rem;
}

.settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.settings-label {
  font-size: .82rem;
  color: var(--qi-ink-muted);
  font-weight: 500;
}
.settings-input-wrap {
  display: flex;
  align-items: center;
  gap: .375rem;
}
.settings-input {
  width: 60px;
  padding: .3rem .5rem;
  border-radius: 7px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-card);
  color: var(--qi-ink);
  font-size: .875rem;
  text-align: center;
  outline: none;
  transition: border-color .2s;
  /* 隐藏数字 spinner */
  -moz-appearance: textfield;
}
.settings-input::-webkit-outer-spin-button,
.settings-input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.settings-input:focus { border-color: var(--qi-primary); }
.settings-unit {
  font-size: .78rem;
  color: var(--qi-ink-light);
}

.settings-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: .125rem;
}
.settings-reset {
  font-size: .75rem;
  color: var(--qi-ink-light);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: color .2s;
}
.settings-reset:hover { color: var(--qi-ink-muted); }
.settings-actions {
  display: flex;
  gap: .5rem;
}
.settings-cancel,
.settings-save {
  padding: .35rem .875rem;
  border-radius: 7px;
  font-size: .8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all .2s;
}
.settings-cancel {
  background: none;
  border: 1.5px solid var(--qi-border);
  color: var(--qi-ink-muted);
}
.settings-cancel:hover { border-color: var(--qi-primary); color: var(--qi-primary); }
.settings-save {
  background: var(--qi-primary);
  border: none;
  color: #fff;
}
.settings-save:hover { opacity: .87; }

/* 设置面板动画 */
.settings-slide-enter-active { transition: opacity .2s, transform .2s; }
.settings-slide-leave-active { transition: opacity .15s, transform .15s; }
.settings-slide-enter-from { opacity: 0; transform: translateY(-6px); }
.settings-slide-leave-to   { opacity: 0; transform: translateY(-6px); }

/* 进度环 */
.ring-wrap {
  position: relative;
  width: 188px;
  height: 188px;
}
.ring-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}
.ring-track {
  fill: none;
  stroke: var(--qi-bg-muted);
  stroke-width: 9;
}
.ring-progress {
  fill: none;
  stroke-width: 9;
  stroke-linecap: round;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
  transition: stroke-dashoffset .4s linear, stroke .3s ease;
}
.ring-progress.work  { stroke: var(--qi-primary); }
.ring-progress.short { stroke: var(--qi-wind); }
.ring-progress.long  { stroke: var(--qi-accent); }

.ring-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: .25rem;
}
.time-display {
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--qi-ink);
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum";
  line-height: 1;
  letter-spacing: .04em;
}
.status-label {
  font-size: .78rem;
  color: var(--qi-ink-muted);
}

/* 控制按钮 */
.controls {
  display: flex;
  gap: .75rem;
  align-items: center;
}
.ctrl-btn {
  border-radius: 999px;
  font-size: .875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all .2s;
}
.reset-btn {
  display: flex;
  align-items: center;
  gap: .35rem;
  padding: .475rem 1rem;
  background: none;
  border: 1.5px solid var(--qi-border);
  color: var(--qi-ink-muted);
}
.reset-btn:hover {
  border-color: var(--qi-primary);
  color: var(--qi-primary);
}
.start-btn {
  padding: .5rem 1.875rem;
  border: none;
  color: #fff;
  min-width: 108px;
  text-align: center;
}
.start-btn.work  { background: var(--qi-primary); }
.start-btn.short { background: var(--qi-wind); }
.start-btn.long  { background: var(--qi-accent); color: var(--qi-ink); }
.start-btn:hover { opacity: .87; }

/* 今日进度 */
.today-row {
  display: flex;
  align-items: center;
  gap: .625rem;
}
.today-label {
  font-size: .78rem;
  color: var(--qi-ink-muted);
}
.cycle-dots {
  display: flex;
  gap: 5px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--qi-border);
  transition: background .25s;
}
.dot.filled { background: var(--qi-primary); }
.today-count {
  font-size: .78rem;
  font-weight: 600;
  color: var(--qi-ink);
}
</style>
