<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Holiday {
  name: string
  type: 'statutory' | 'traditional' | 'cultural'
}
interface CalendarEvent {
  title: string
  detail?: string
}
type EventStore = Record<string, CalendarEvent[]>

const HOLIDAY_DB: Record<string, Holiday[]> = {
  '01-01': [{ name: '元旦', type: 'statutory' }],
  '02-14': [{ name: '情人节', type: 'cultural' }],
  '03-08': [{ name: '妇女节', type: 'cultural' }],
  '05-01': [{ name: '劳动节', type: 'statutory' }],
  '06-01': [{ name: '儿童节', type: 'cultural' }],
  '09-10': [{ name: '教师节', type: 'cultural' }],
  '10-01': [{ name: '国庆节', type: 'statutory' }],
  '12-24': [{ name: '平安夜', type: 'cultural' }],
  '12-25': [{ name: '圣诞节', type: 'cultural' }],
  '2025-01-29': [{ name: '春节', type: 'statutory' }],
  '2025-02-12': [{ name: '元宵节', type: 'traditional' }],
  '2025-04-04': [{ name: '清明节', type: 'statutory' }],
  '2025-05-31': [{ name: '端午节', type: 'statutory' }],
  '2025-10-06': [{ name: '中秋节', type: 'statutory' }],
  '2026-02-17': [{ name: '春节', type: 'statutory' }],
  '2026-03-03': [{ name: '元宵节', type: 'traditional' }],
  '2026-04-05': [{ name: '清明节', type: 'statutory' }],
  '2026-06-19': [{ name: '端午节', type: 'statutory' }],
  '2026-10-03': [{ name: '中秋节', type: 'statutory' }],
  '2027-02-06': [{ name: '春节', type: 'statutory' }],
  '2027-02-20': [{ name: '元宵节', type: 'traditional' }],
  '2027-04-05': [{ name: '清明节', type: 'statutory' }],
}

function getHolidays(dateStr: string): Holiday[] {
  return [...(HOLIDAY_DB[dateStr] ?? []), ...(HOLIDAY_DB[dateStr.slice(5)] ?? [])]
}

const PRESET_EVENTS = ['考试', '出差', '旅游', '约会', '聚会', '体检', '会议', '生日']

// ── 实时时钟 ──────────────────────────────────────────────────────────
const now = ref(new Date())
let clockTimer: ReturnType<typeof setInterval>
onMounted(() => { clockTimer = setInterval(() => { now.value = new Date() }, 1000) })
onUnmounted(() => clearInterval(clockTimer))

const WEEKDAY_NAMES = ['周日','周一','周二','周三','周四','周五','周六']
const MONTHS = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
const WEEKDAYS = ['一','二','三','四','五','六','日']

const timeStr = computed(() => {
  const d = now.value, p = (n: number) => String(n).padStart(2, '0')
  return `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
})
const weekdayStr = computed(() => WEEKDAY_NAMES[now.value.getDay()])

// ── 个人日程 (localStorage) ───────────────────────────────────────────
const STORAGE_KEY = 'qi-calendar-events'
const events = ref<EventStore>({})

onMounted(() => {
  try {
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}')
    const migrated: EventStore = {}
    for (const [k, v] of Object.entries(raw)) {
      if (Array.isArray(v)) {
        migrated[k] = v.map(item =>
          typeof item === 'string' ? { title: item } : item as CalendarEvent
        )
      }
    }
    events.value = migrated
  } catch {}
})

function saveEvents() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(events.value))
}

const newTitle = ref('')
const newDetail = ref('')
const detailRef = ref<HTMLTextAreaElement | null>(null)

function selectPreset(type: string) {
  newTitle.value = newTitle.value === type ? '' : type
}

function clearForm() {
  newTitle.value = ''
  newDetail.value = ''
}

function addEvent() {
  const title = newTitle.value.trim()
  if (!title || selectedDay.value === null) return
  const key = toDateStr(selectedDay.value)
  const ev: CalendarEvent = { title }
  if (newDetail.value.trim()) ev.detail = newDetail.value.trim()
  events.value = { ...events.value, [key]: [...(events.value[key] ?? []), ev] }
  saveEvents()
  clearForm()
}

function removeEvent(day: number, idx: number) {
  const key = toDateStr(day)
  const list = (events.value[key] ?? []).filter((_, i) => i !== idx)
  const updated = { ...events.value }
  if (list.length) updated[key] = list
  else delete updated[key]
  events.value = updated
  saveEvents()
}

// ── 日历状态 ──────────────────────────────────────────────────────────
const viewYear = ref(now.value.getFullYear())
const viewMonth = ref(now.value.getMonth())
const selectedDay = ref<number | null>(null)

const daysInMonth = computed(() => new Date(viewYear.value, viewMonth.value + 1, 0).getDate())
const startOffset = computed(() => (new Date(viewYear.value, viewMonth.value, 1).getDay() + 6) % 7)

const calendarCells = computed(() => {
  const cells: (number | null)[] = []
  for (let i = 0; i < startOffset.value; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth.value; d++) cells.push(d)
  while (cells.length % 7 !== 0) cells.push(null)
  return cells
})

const isCurrentMonth = computed(() =>
  viewYear.value === now.value.getFullYear() && viewMonth.value === now.value.getMonth()
)
const isToday = (day: number | null) => {
  if (!day) return false
  const t = now.value
  return day === t.getDate() && viewMonth.value === t.getMonth() && viewYear.value === t.getFullYear()
}

function toDateStr(day: number) {
  return `${viewYear.value}-${String(viewMonth.value + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`
}

function dayHolidays(day: number): Holiday[] {
  return getHolidays(toDateStr(day))
}
function dayEvents(day: number): CalendarEvent[] {
  return events.value[toDateStr(day)] ?? []
}

function prevMonth() {
  if (viewMonth.value === 0) { viewMonth.value = 11; viewYear.value-- }
  else viewMonth.value--
  selectedDay.value = null
}
function nextMonth() {
  if (viewMonth.value === 11) { viewMonth.value = 0; viewYear.value++ }
  else viewMonth.value++
  selectedDay.value = null
}
function goToday() {
  viewYear.value = now.value.getFullYear()
  viewMonth.value = now.value.getMonth()
  selectedDay.value = null
}
function selectDay(day: number | null) {
  if (!day) return
  selectedDay.value = selectedDay.value === day ? null : day
  clearForm()
}
function closeModal() {
  selectedDay.value = null
  clearForm()
}

// ── 弹窗计算属性 ──────────────────────────────────────────────────────
const selHolidays = computed(() =>
  selectedDay.value !== null ? dayHolidays(selectedDay.value) : []
)
const selEvents = computed(() =>
  selectedDay.value !== null ? dayEvents(selectedDay.value) : []
)
const selWeekday = computed(() => {
  if (selectedDay.value === null) return ''
  return WEEKDAY_NAMES[new Date(viewYear.value, viewMonth.value, selectedDay.value).getDay()]
})
</script>

<template>
  <div class="calendar-widget">
    <!-- 时钟区 -->
    <div class="clock-area">
      <div class="clock-time">{{ timeStr }}</div>
      <div class="clock-date">
        {{ now.getFullYear() }} 年 {{ now.getMonth() + 1 }} 月 {{ now.getDate() }} 日 · {{ weekdayStr }}
      </div>
    </div>

    <!-- 月份导航 -->
    <div class="month-nav">
      <button class="nav-btn" @click="prevMonth" aria-label="上个月">‹</button>
      <div class="month-label">
        <span class="month-year">{{ viewYear }}</span>
        <span class="month-name">{{ MONTHS[viewMonth] }}</span>
        <button v-if="!isCurrentMonth" class="today-btn" @click="goToday">今天</button>
      </div>
      <button class="nav-btn" @click="nextMonth" aria-label="下个月">›</button>
    </div>

    <!-- 星期头 -->
    <div class="weekday-row">
      <span v-for="(d, i) in WEEKDAYS" :key="d" :class="{ weekend: i >= 5 }">{{ d }}</span>
    </div>

    <!-- 日历格 -->
    <div class="day-grid">
      <div
        v-for="(day, idx) in calendarCells"
        :key="idx"
        class="day-cell"
        :class="{
          empty: day === null,
          today: isToday(day),
          selected: selectedDay === day && day !== null,
          weekend: idx % 7 >= 5 && day !== null,
        }"
        @click="selectDay(day)"
      >
        <template v-if="day !== null">
          <span class="day-num">{{ day }}</span>
          <span
            v-if="dayHolidays(day).length"
            class="cell-holiday"
            :class="dayHolidays(day)[0].type"
          >{{ dayHolidays(day)[0].name }}</span>
          <template v-if="dayEvents(day).length">
            <span class="cell-event">{{ dayEvents(day)[0].title }}</span>
            <span v-if="dayEvents(day).length > 1" class="cell-more">
              +{{ dayEvents(day).length - 1 }}
            </span>
          </template>
        </template>
      </div>
    </div>
  </div>

  <!-- 日程弹窗 (Teleport 到 body 避免层叠上下文问题) -->
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="selectedDay !== null"
        class="modal-backdrop"
        @click.self="closeModal"
      >
        <div class="modal-box" role="dialog" :aria-label="`${viewMonth + 1}月${selectedDay}日日程`">
          <!-- 弹窗头 -->
          <div class="modal-header">
            <div class="modal-title">
              <span class="modal-date">{{ viewMonth + 1 }}月{{ selectedDay }}日</span>
              <span class="modal-weekday">{{ selWeekday }}</span>
            </div>
            <button class="modal-close" @click="closeModal" aria-label="关闭">×</button>
          </div>

          <!-- 节假日 -->
          <div v-if="selHolidays.length" class="modal-holidays">
            <span
              v-for="h in selHolidays"
              :key="h.name"
              class="holiday-badge"
              :class="h.type"
            >{{ h.name }}</span>
          </div>

          <!-- 已有日程 -->
          <div v-if="selEvents.length" class="modal-events">
            <div v-for="(ev, i) in selEvents" :key="i" class="event-card">
              <div class="event-card-header">
                <span class="event-chip">{{ ev.title }}</span>
                <button class="event-del" @click="removeEvent(selectedDay!, i)" aria-label="删除">×</button>
              </div>
              <p v-if="ev.detail" class="event-detail">{{ ev.detail }}</p>
            </div>
          </div>

          <div v-if="selEvents.length" class="modal-divider" />

          <!-- 添加日程 -->
          <div class="add-section">
            <p class="add-label">添加日程</p>
            <div class="preset-grid">
              <button
                v-for="type in PRESET_EVENTS"
                :key="type"
                class="preset-btn"
                :class="{ active: newTitle === type }"
                @click="selectPreset(type)"
              >{{ type }}</button>
            </div>
            <div class="event-form">
              <div class="form-row">
                <input
                  v-model="newTitle"
                  class="title-input"
                  placeholder="标题（最多 4 字）"
                  maxlength="4"
                  @keydown.enter.prevent="detailRef?.focus()"
                />
                <button
                  v-if="newTitle || newDetail"
                  class="clear-btn"
                  @click="clearForm"
                  aria-label="清空"
                >×</button>
              </div>
              <textarea
                ref="detailRef"
                v-model="newDetail"
                class="detail-textarea"
                placeholder="详细说明（可选）&#10;时间、地点、注意事项..."
                rows="3"
                maxlength="300"
              />
              <div class="form-footer">
                <span class="detail-count">{{ newDetail.length }}/300</span>
                <button
                  class="submit-btn"
                  :disabled="!newTitle.trim()"
                  @click="addEvent"
                >添加日程</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.calendar-widget { width: 100%; }

/* 时钟 */
.clock-area {
  text-align: center;
  padding: 1.5rem 1rem 1.25rem;
  border-bottom: 1px solid var(--qi-border);
}
.clock-time {
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: .08em;
  color: var(--qi-ink);
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum";
  line-height: 1;
  margin-bottom: .5rem;
}
.clock-date { font-size: .85rem; color: var(--qi-ink-muted); }

/* 月份导航 */
.month-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: .75rem 1rem;
}
.nav-btn {
  width: 28px; height: 28px;
  border-radius: 50%;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-muted);
  color: var(--qi-ink-muted);
  cursor: pointer;
  font-size: 1.2rem;
  display: flex; align-items: center; justify-content: center;
  transition: border-color .2s, color .2s;
}
.nav-btn:hover { border-color: var(--qi-primary); color: var(--qi-primary); }
.month-label { display: flex; align-items: center; gap: .5rem; }
.month-year { font-size: .875rem; color: var(--qi-ink-muted); }
.month-name { font-size: 1.1rem; font-weight: 600; color: var(--qi-ink); }
.today-btn {
  font-size: .72rem; padding: 2px 8px;
  border-radius: 999px;
  border: 1.5px solid var(--qi-primary);
  color: var(--qi-primary);
  background: none; cursor: pointer;
  transition: background .2s, color .2s;
}
.today-btn:hover { background: var(--qi-primary); color: #fff; }

/* 星期头 */
.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  padding: 0 .5rem;
}
.weekday-row span {
  text-align: center;
  font-size: .72rem; font-weight: 600;
  color: var(--qi-ink-muted);
  padding: .3rem 0;
}
.weekday-row span.weekend { color: var(--qi-soft); }

/* 日历格 */
.day-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  padding: 0 .5rem .75rem;
}
.day-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 4px 1px 3px;
  min-height: 60px;
  border-radius: 6px;
  cursor: pointer;
  transition: background .15s;
  overflow: hidden;
}
.day-cell.empty { pointer-events: none; }
.day-cell:not(.empty):hover { background: var(--qi-bg-muted); }

.day-num { font-size: .85rem; font-weight: 500; color: var(--qi-ink); line-height: 1.3; }
.day-cell.weekend .day-num { color: var(--qi-soft); }

.cell-holiday {
  font-size: .6rem; line-height: 1.2; font-weight: 500;
  text-align: center; max-width: 100%;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  padding: 0 1px;
}
.cell-holiday.statutory { color: var(--qi-primary); }
.cell-holiday.traditional, .cell-holiday.cultural { color: var(--qi-ink-muted); }

.cell-event {
  font-size: .58rem; padding: 1px 3px; border-radius: 3px;
  background: rgba(255, 140, 90, 0.15);
  color: var(--qi-primary);
  max-width: calc(100% - 2px);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  margin-top: 1px; line-height: 1.4;
}
.cell-more { font-size: .52rem; color: var(--qi-ink-light); line-height: 1.2; }

.day-cell.selected:not(.today) {
  background: rgba(255, 140, 90, 0.1);
  box-shadow: inset 0 0 0 1.5px var(--qi-primary);
}
.day-cell.today { background: var(--qi-primary) !important; }
.day-cell.today .day-num { color: #fff; font-weight: 700; }
.day-cell.today .cell-holiday { color: rgba(255,255,255,0.9) !important; }
.day-cell.today .cell-event { background: rgba(255,255,255,0.25); color: #fff; }
.day-cell.today .cell-more { color: rgba(255,255,255,0.7); }

/* ── 弹窗 ─────────────────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(58, 42, 26, 0.28);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
}

.modal-box {
  background: var(--qi-bg-card);
  border: 1px solid var(--qi-border);
  border-radius: 18px;
  box-shadow: 0 12px 48px rgba(58, 42, 26, 0.16);
  width: 100%;
  max-width: 360px;
  max-height: 85vh;
  overflow-y: auto;
  padding: 1.25rem;
  scrollbar-width: thin;
}

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: .875rem;
}
.modal-title { display: flex; align-items: baseline; gap: .4rem; }
.modal-date { font-size: 1.1rem; font-weight: 700; color: var(--qi-ink); }
.modal-weekday { font-size: .85rem; color: var(--qi-ink-muted); }
.modal-close {
  width: 28px; height: 28px; border-radius: 50%;
  border: 1.5px solid var(--qi-border); background: none;
  color: var(--qi-ink-muted); cursor: pointer;
  font-size: 1.1rem; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s; flex-shrink: 0;
}
.modal-close:hover { border-color: var(--qi-primary); color: var(--qi-primary); }

.modal-holidays { display: flex; flex-wrap: wrap; gap: .375rem; margin-bottom: .875rem; }
.holiday-badge { font-size: .75rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.holiday-badge.statutory { background: rgba(255, 140, 90, 0.15); color: var(--qi-primary); }
.holiday-badge.traditional { background: rgba(255, 209, 102, 0.25); color: var(--qi-ink); }
.holiday-badge.cultural { background: rgba(168, 216, 192, 0.3); color: var(--qi-ink); }

.modal-events { display: flex; flex-direction: column; gap: .5rem; margin-bottom: .875rem; }
.event-card {
  background: rgba(255, 140, 90, 0.07);
  border: 1px solid rgba(255, 140, 90, 0.18);
  border-radius: 10px;
  padding: .5rem .75rem;
}
.event-card-header { display: flex; align-items: center; justify-content: space-between; }
.event-chip { font-size: .85rem; font-weight: 600; color: var(--qi-primary); }
.event-detail {
  font-size: .8rem; color: var(--qi-ink-muted);
  margin-top: .3rem; line-height: 1.6;
  white-space: pre-wrap; word-break: break-all;
}
.event-del {
  width: 18px; height: 18px; border-radius: 50%;
  border: none; background: rgba(255, 140, 90, 0.15);
  color: var(--qi-primary); cursor: pointer;
  font-size: .8rem; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s; flex-shrink: 0;
}
.event-del:hover { background: var(--qi-primary); color: #fff; }

.modal-divider { border: none; border-top: 1px solid var(--qi-border); margin-bottom: .875rem; }

/* 添加表单 */
.add-label { font-size: .78rem; font-weight: 600; color: var(--qi-ink-muted); margin-bottom: .5rem; }
.preset-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: .375rem;
  margin-bottom: .75rem;
}
.preset-btn {
  padding: .375rem .25rem;
  border-radius: 8px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-muted);
  color: var(--qi-ink-muted);
  font-size: .82rem;
  cursor: pointer; text-align: center;
  transition: all .2s;
}
.preset-btn:hover,
.preset-btn.active {
  border-color: var(--qi-primary);
  color: var(--qi-primary);
  background: rgba(255, 140, 90, 0.08);
}

.event-form { display: flex; flex-direction: column; gap: .5rem; }
.form-row { display: flex; gap: .5rem; align-items: center; }
.title-input {
  flex: 1; padding: .425rem .675rem;
  border-radius: 8px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-muted);
  color: var(--qi-ink); font-size: .875rem;
  outline: none; transition: border-color .2s;
}
.title-input:focus { border-color: var(--qi-primary); }
.title-input::placeholder { color: var(--qi-ink-light); }
.clear-btn {
  width: 26px; height: 26px; border-radius: 50%;
  border: 1px solid var(--qi-border); background: none;
  color: var(--qi-ink-muted); cursor: pointer;
  font-size: .9rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all .15s;
}
.clear-btn:hover { border-color: #e05555; color: #e05555; }

.detail-textarea {
  width: 100%; padding: .5rem .675rem;
  border-radius: 8px;
  border: 1.5px solid var(--qi-border);
  background: var(--qi-bg-muted);
  color: var(--qi-ink); font-size: .82rem;
  outline: none; resize: none;
  transition: border-color .2s;
  line-height: 1.55;
  box-sizing: border-box;
  font-family: inherit;
}
.detail-textarea:focus { border-color: var(--qi-primary); }
.detail-textarea::placeholder { color: var(--qi-ink-light); }

.form-footer { display: flex; align-items: center; justify-content: space-between; }
.detail-count { font-size: .72rem; color: var(--qi-ink-light); }
.submit-btn {
  padding: .4rem 1.125rem;
  border-radius: 8px; border: none;
  background: var(--qi-primary); color: #fff;
  font-size: .84rem; font-weight: 500;
  cursor: pointer; transition: opacity .2s;
}
.submit-btn:hover:not(:disabled) { opacity: .85; }
.submit-btn:disabled { opacity: .4; cursor: default; }

/* 弹窗动画 */
.modal-enter-active { transition: opacity .2s, transform .2s; }
.modal-leave-active { transition: opacity .15s, transform .15s; }
.modal-enter-from { opacity: 0; transform: scale(.96); }
.modal-leave-to { opacity: 0; transform: scale(.96); }
</style>
