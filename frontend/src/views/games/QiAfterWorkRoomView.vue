<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { assetUrl } from '@/utils/assets'

type RoomAction = {
  id: string
  label: string
  detail: string
  result: string
  energy: number
  mood: number
  stress: number
  taskId?: string
}

type RoomSpot = {
  id: string
  name: string
  hint: string
  x: number
  y: number
  width: number
  height: number
  actions: RoomAction[]
}

const router = useRouter()
const roomImage = assetUrl('/games/qi-after-work/room/Room_Base.png')

const energy = ref(72)
const mood = ref(66)
const stress = ref(28)
const hour = ref(9)
const minute = ref(0)
const selectedSpotId = ref<string | null>(null)
const showTasks = ref(false)
const showSummary = ref(false)
const lastResult = ref('')
const completedActions = ref<string[]>([])
let resultTimer: ReturnType<typeof window.setTimeout> | undefined

const tasks = ref([
  { id: 'bug', label: '处理一个难缠的 Bug', note: '书桌', done: false },
  { id: 'note', label: '写下一段今天的想法', note: '书桌', done: false },
  { id: 'rest', label: '给自己留一点空白', note: '沙发或窗边', done: false },
])

onMounted(() => {
  document.body.classList.add('qi-after-work-active')
})

onUnmounted(() => {
  document.body.classList.remove('qi-after-work-active')
  if (resultTimer) window.clearTimeout(resultTimer)
})

const spots: RoomSpot[] = [
  {
    id: 'window', name: '窗边', hint: '看看外面', x: 1, y: 5, width: 11, height: 48,
    actions: [
      { id: 'window-rest', label: '看一会儿天空', detail: '让脑袋安静下来。', result: '窗外的云走得很慢，事情也可以慢一点。', energy: 0, mood: 7, stress: -10, taskId: 'rest' },
    ],
  },
  {
    id: 'fridge', name: '冰箱', hint: '找点吃的', x: 31, y: 25, width: 10, height: 32,
    actions: [
      { id: 'fridge-fruit', label: '吃一块水果', detail: '西瓜听起来不错。', result: '冰凉的水果让心情恢复了一点。', energy: 8, mood: 9, stress: -3 },
      { id: 'fridge-water', label: '喝杯水', detail: '短暂补充一下。', result: '喝完水，感觉稍微清醒了。', energy: 4, mood: 1, stress: -2 },
    ],
  },
  {
    id: 'sofa', name: '沙发', hint: '休息一下', x: 40, y: 39, width: 17, height: 20,
    actions: [
      { id: 'sofa-rest', label: '发一会儿呆', detail: '不做任何事也是安排。', result: '沙发非常理解今天的你。', energy: 7, mood: 5, stress: -8, taskId: 'rest' },
      { id: 'sofa-music', label: '听一首歌', detail: '只听一首。', result: '这一首歌正好听完，没有循环到忘记时间。', energy: 0, mood: 10, stress: -4 },
    ],
  },
  {
    id: 'desk', name: '书桌', hint: '处理点事情', x: 57, y: 34, width: 15, height: 25,
    actions: [
      { id: 'desk-code', label: '修一个 Bug', detail: '先从最奇怪的报错开始。', result: 'Bug 暂时安静了，至少看起来是这样。', energy: -13, mood: 4, stress: 9, taskId: 'bug' },
      { id: 'desk-note', label: '写一点东西', detail: '把脑袋里的碎片记下来。', result: '写下来的想法好像比刚才完整了一点。', energy: -8, mood: 8, stress: 1, taskId: 'note' },
    ],
  },
  {
    id: 'bookshelf', name: '书架', hint: '翻翻收藏', x: 72, y: 16, width: 9, height: 46,
    actions: [
      { id: 'bookshelf-read', label: '随便翻一本书', detail: '不需要读完。', result: '翻到一页很适合今天的话。', energy: 1, mood: 5, stress: -5 },
    ],
  },
  {
    id: 'bed', name: '床', hint: '躺一下', x: 81, y: 39, width: 18, height: 26,
    actions: [
      { id: 'bed-nap', label: '睡个短觉', detail: '定好闹钟，真的。', result: '醒来时没有错过整个下午，真难得。', energy: 18, mood: 4, stress: -12 },
      { id: 'bed-sleep', label: '今天先到这里', detail: '把剩下的事交给明天。', result: '水豚祁决定先睡觉，明天的事情明天再说。', energy: 25, mood: 7, stress: -18 },
    ],
  },
  {
    id: 'door', name: '门口', hint: '看看有什么动静', x: 17, y: 17, width: 10, height: 39,
    actions: [
      { id: 'door-package', label: '去拿快递', detail: '希望不是新的安排。', result: '是一个小包裹，不是临时会议。', energy: -3, mood: 7, stress: -2 },
    ],
  },
]

const selectedSpot = computed(() => spots.find((spot) => spot.id === selectedSpotId.value) ?? null)
const doneTaskCount = computed(() => tasks.value.filter((task) => task.done).length)
const dayGrade = computed(() => {
  const score = doneTaskCount.value * 20 + Math.round(mood.value * .35) + Math.round(energy.value * .15) - Math.round(stress.value * .25)
  if (score >= 85) return '今天过得很好'
  if (score >= 60) return '今天也算顺利'
  return '今天辛苦了'
})

const timeLabel = computed(() => `${String(hour.value).padStart(2, '0')}:${String(minute.value).padStart(2, '0')}`)
const phase = computed(() => {
  if (hour.value < 12) return '早晨'
  if (hour.value < 17) return '午后'
  if (hour.value < 20) return '傍晚'
  return '夜晚'
})

function cap(value: number) {
  return Math.max(0, Math.min(100, value))
}

function selectSpot(id: string) {
  selectedSpotId.value = id
}

function advanceTime(hours = 1) {
  const total = hour.value * 60 + minute.value + hours * 60
  hour.value = Math.min(23, Math.floor(total / 60) % 24)
  minute.value = total % 60
}

function runAction(action: RoomAction) {
  energy.value = cap(energy.value + action.energy)
  mood.value = cap(mood.value + action.mood)
  stress.value = cap(stress.value + action.stress)
  advanceTime(action.id === 'bed-sleep' ? 3 : 1)
  completedActions.value.unshift(`${timeLabel.value} · ${action.label}`)
  completedActions.value = completedActions.value.slice(0, 8)
  if (action.taskId) {
    const task = tasks.value.find((item) => item.id === action.taskId)
    if (task) task.done = true
  }
  lastResult.value = action.result
  if (resultTimer) window.clearTimeout(resultTimer)
  resultTimer = window.setTimeout(() => { lastResult.value = '' }, 3200)
  selectedSpotId.value = null

  if (action.id === 'bed-sleep' || hour.value >= 22) {
    window.setTimeout(() => { showSummary.value = true }, 180)
  }
}

function restartDay() {
  energy.value = 72
  mood.value = 66
  stress.value = 28
  hour.value = 9
  minute.value = 0
  selectedSpotId.value = null
  tasks.value.forEach((task) => { task.done = false })
  completedActions.value = []
  lastResult.value = ''
  if (resultTimer) window.clearTimeout(resultTimer)
  showTasks.value = false
  showSummary.value = false
}
</script>

<template>
  <div class="after-work-page">
    <header class="game-header">
      <button class="icon-button" type="button" title="返回游戏区" aria-label="返回游戏区" @click="router.push('/games')">←</button>
      <div class="game-title">
        <p>水豚祁的房间</p>
        <h1>下班计划</h1>
      </div>
      <div class="header-tools">
        <button class="task-button" type="button" @click="showTasks = !showTasks">待办 {{ doneTaskCount }}/{{ tasks.length }}</button>
        <button class="reset-button" type="button" title="重置今天" aria-label="重置今天" @click="restartDay">↻</button>
      </div>
    </header>

    <section class="status-strip" aria-label="今日状态">
      <div class="day-state"><span>{{ phase }}</span><strong>{{ timeLabel }}</strong></div>
      <div class="stat"><span>精力</span><div><i :style="{ width: `${energy}%` }"></i></div><b>{{ energy }}</b></div>
      <div class="stat mood"><span>心情</span><div><i :style="{ width: `${mood}%` }"></i></div><b>{{ mood }}</b></div>
      <div class="stat stress"><span>压力</span><div><i :style="{ width: `${stress}%` }"></i></div><b>{{ stress }}</b></div>
    </section>

    <main class="room-shell">
      <div class="room-stage" :class="`phase-${phase}`">
        <img :src="roomImage" class="room-image" alt="水豚祁的房间" draggable="false" />
        <div class="sun-wash"></div>

        <button
          v-for="spot in spots"
          :key="spot.id"
          class="room-hotspot"
          :class="{ selected: selectedSpotId === spot.id }"
          :style="{ left: `${spot.x}%`, top: `${spot.y}%`, width: `${spot.width}%`, height: `${spot.height}%` }"
          type="button"
          @click="selectSpot(spot.id)"
        >
          <span>{{ spot.name }}</span>
          <small>{{ spot.hint }}</small>
        </button>

        <Transition name="action-panel">
          <aside v-if="selectedSpot" class="action-panel" aria-live="polite">
            <div class="panel-heading">
              <div><span>{{ selectedSpot.hint }}</span><h2>{{ selectedSpot.name }}</h2></div>
              <button type="button" aria-label="关闭" @click="selectedSpotId = null">×</button>
            </div>
            <button v-for="action in selectedSpot.actions" :key="action.id" class="action-button" type="button" @click="runAction(action)">
              <strong>{{ action.label }}</strong>
              <span>{{ action.detail }}</span>
            </button>
          </aside>
        </Transition>

        <Transition name="task-panel">
          <aside v-if="showTasks" class="task-panel" aria-label="今日待办">
            <div class="panel-heading">
              <div><span>今天只做这些就够了</span><h2>今日待办</h2></div>
              <button type="button" aria-label="关闭待办" @click="showTasks = false">×</button>
            </div>
            <ul>
              <li v-for="task in tasks" :key="task.id" :class="{ done: task.done }">
                <i>{{ task.done ? '✓' : '' }}</i>
                <span><strong>{{ task.label }}</strong><small>{{ task.note }}</small></span>
              </li>
            </ul>
          </aside>
        </Transition>

        <Transition name="result-toast">
          <p v-if="lastResult && !selectedSpot" class="result-toast">{{ lastResult }}</p>
        </Transition>

        <Transition name="summary">
          <div v-if="showSummary" class="summary-mask" role="dialog" aria-modal="true" aria-label="今日结算">
            <section class="summary-card">
              <p class="summary-kicker">{{ phase }} · {{ timeLabel }}</p>
              <h2>{{ dayGrade }}</h2>
              <p class="summary-copy">完成 {{ doneTaskCount }}/{{ tasks.length }} 项待办，剩下的事可以留给明天。</p>
              <div class="summary-stats"><span>精力 <b>{{ energy }}</b></span><span>心情 <b>{{ mood }}</b></span><span>压力 <b>{{ stress }}</b></span></div>
              <div v-if="completedActions.length" class="summary-log"><p v-for="item in completedActions.slice(0, 4)" :key="item">{{ item }}</p></div>
              <button type="button" @click="restartDay">开始新的一天</button>
              <button type="button" class="summary-close" @click="showSummary = false">继续看看房间</button>
            </section>
          </div>
        </Transition>
      </div>
    </main>
  </div>
</template>

<style scoped>
:global(body.qi-after-work-active),:global(body.qi-after-work-active #app),:global(body.qi-after-work-active main) { height:100dvh; overflow:hidden; }
.after-work-page { position:relative; width:100%; height:100dvh; overflow:hidden; background:#ecbd7c; color:#5c422b; isolation:isolate; }
.game-header { position:absolute; z-index:5; top:max(14px,env(safe-area-inset-top)); left:16px; right:16px; display:flex; align-items:center; justify-content:space-between; pointer-events:none; }
.icon-button,.reset-button,.task-button { pointer-events:auto; border:1px solid rgba(255,249,234,.54); background:rgba(97,65,36,.28); box-shadow:0 4px 14px rgba(86,52,24,.16); color:#fffaf0; backdrop-filter:blur(7px); cursor:pointer; }
.icon-button { display:grid; width:40px; height:40px; place-items:center; border-radius:50%; font-size:23px; line-height:1; }.header-tools { display:flex; align-items:center; gap:7px; pointer-events:auto; }.reset-button { display:grid; width:36px; height:36px; place-items:center; border-radius:50%; font-size:19px; line-height:1; }.task-button { padding:8px 10px; border-radius:6px; font-size:12px; }.icon-button:hover,.reset-button:hover,.task-button:hover { background:rgba(97,65,36,.45); }
.game-title { position:absolute; left:50%; transform:translateX(-50%); min-width:150px; padding:6px 15px 7px; border:1px solid rgba(255,249,234,.38); border-radius:5px; background:rgba(255,250,237,.74); box-shadow:0 5px 16px rgba(89,55,23,.1); text-align:center; line-height:1.1; }.game-title p { margin:0 0 3px; font-size:10px; color:#9e7450; }.game-title h1 { margin:0; font:600 18px/1.1 'Noto Serif SC',serif; letter-spacing:0; }
.status-strip { position:absolute; z-index:5; top:72px; left:50%; display:grid; width:min(610px,calc(100% - 32px)); grid-template-columns:116px repeat(3,1fr); gap:10px; align-items:center; padding:8px 11px; transform:translateX(-50%); border:1px solid rgba(255,249,234,.38); border-radius:6px; background:rgba(255,250,237,.78); box-shadow:0 6px 18px rgba(89,55,23,.1); backdrop-filter:blur(6px); }
.day-state { display:flex; align-items:center; gap:8px; padding-right:10px; border-right:1px solid rgba(133,92,52,.14); }.day-state span { font-size:11px; color:#9d7857; }.day-state strong { font-size:16px; letter-spacing:0; }.stat { display:grid; grid-template-columns:28px 1fr 22px; align-items:center; gap:5px; font-size:11px; color:#8a674a; }.stat > div { height:6px; overflow:hidden; border-radius:20px; background:#f2dfc6; }.stat i { display:block; height:100%; border-radius:inherit; background:#e9a56d; transition:width .35s ease; }.stat b { font-size:11px; font-weight:600; color:#6d4a30; }.mood i { background:#e89b9b; }.stress i { background:#94b48a; }
.room-shell { position:absolute; inset:0; z-index:0; }.room-stage { position:relative; width:100%; height:100%; overflow:hidden; background:#f4ddb9; isolation:isolate; }.room-image { display:block; width:100%; height:100%; object-fit:cover; object-position:center; user-select:none; }.sun-wash { position:absolute; inset:0; z-index:1; pointer-events:none; background:rgba(255,240,196,.03); transition:background .4s ease; }.phase-傍晚 .sun-wash { background:rgba(243,133,77,.16); mix-blend-mode:multiply; }.phase-夜晚 .sun-wash { background:rgba(35,57,94,.38); mix-blend-mode:multiply; }.phase-午后 .sun-wash { background:rgba(255,230,151,.05); }
.room-hotspot { position:absolute; z-index:2; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:0; border:0; outline:0; background:transparent; color:#6b4630; cursor:pointer; }.room-hotspot span,.room-hotspot small { opacity:0; pointer-events:none; transition:opacity .16s ease,transform .16s ease; }.room-hotspot span { padding:2px 7px; border-radius:4px; background:rgba(255,251,241,.94); box-shadow:0 2px 8px rgba(92,58,29,.12); font-size:12px; font-weight:700; transform:translateY(3px); }.room-hotspot small { margin-top:3px; font-size:10px; color:#8a684d; }.room-hotspot:hover span,.room-hotspot:hover small,.room-hotspot:focus-visible span,.room-hotspot:focus-visible small { opacity:1; }.room-hotspot:hover span,.room-hotspot:focus-visible span { transform:translateY(0); }.room-hotspot:focus-visible { box-shadow:inset 0 0 0 2px rgba(255,250,235,.86); border-radius:4px; }
.action-panel,.task-panel { position:absolute; z-index:6; width:min(330px,calc(100% - 40px)); padding:15px; border:1px solid rgba(255,249,234,.55); border-radius:7px; background:rgba(255,250,240,.94); box-shadow:0 15px 36px rgba(84,54,29,.23); backdrop-filter:blur(10px); }.action-panel { right:20px; bottom:22px; }.task-panel { top:128px; right:20px; }.panel-heading { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; }.panel-heading span { font-size:11px; color:#ab805c; }.panel-heading h2 { margin:1px 0 0; font:600 19px/1.2 'Noto Serif SC',serif; }.panel-heading button { border:0; background:transparent; color:#987252; font-size:21px; line-height:1; cursor:pointer; }.action-button { display:block; width:100%; margin-top:7px; padding:10px 11px; border:1px solid rgba(152,104,61,.18); border-radius:5px; background:#fff6e8; color:#684631; text-align:left; cursor:pointer; }.action-button:hover { background:#ffebd2; border-color:rgba(178,108,58,.45); }.action-button strong,.action-button span { display:block; }.action-button strong { font-size:13px; }.action-button span { margin-top:2px; font-size:11px; color:#987456; }.task-panel ul { display:grid; gap:7px; margin:0; padding:0; list-style:none; }.task-panel li { display:flex; align-items:center; gap:9px; padding:8px; border:1px solid rgba(152,104,61,.12); border-radius:5px; }.task-panel li i { display:grid; width:17px; height:17px; place-items:center; flex:0 0 auto; border:1px solid #c9a67e; border-radius:50%; color:#fff; font-size:11px; font-style:normal; }.task-panel li.done { background:#f0f7e9; }.task-panel li.done i { border-color:#8fb17c; background:#8fb17c; }.task-panel li strong,.task-panel li small { display:block; }.task-panel li strong { font-size:12px; font-weight:600; }.task-panel li small { margin-top:1px; color:#9b795a; font-size:10px; }
.result-toast { position:absolute; z-index:5; left:50%; bottom:25px; max-width:min(560px,calc(100% - 40px)); margin:0; padding:9px 13px; transform:translateX(-50%); border-left:3px solid #dfaa75; background:rgba(255,250,241,.9); box-shadow:0 5px 16px rgba(85,52,25,.15); color:#775239; font-size:13px; backdrop-filter:blur(6px); pointer-events:none; }.result-toast-enter-active,.result-toast-leave-active { transition:opacity .25s ease,transform .25s ease; }.result-toast-enter-from,.result-toast-leave-to { opacity:0; transform:translate(-50%,8px); }
.summary-mask { position:absolute; z-index:10; inset:0; display:grid; place-items:center; padding:20px; background:rgba(68,48,30,.35); backdrop-filter:blur(3px); }.summary-card { width:min(390px,100%); padding:25px; border:1px solid rgba(157,107,61,.28); border-radius:8px; background:#fff9ee; box-shadow:0 18px 48px rgba(56,37,20,.3); text-align:center; }.summary-kicker { margin:0; color:#a77b54; font-size:12px; }.summary-card h2 { margin:7px 0; font:600 26px/1.2 'Noto Serif SC',serif; }.summary-copy { margin:0; color:#856345; font-size:13px; }.summary-stats { display:flex; justify-content:space-between; gap:7px; margin:17px 0 10px; padding:9px; border-radius:5px; background:#fff0dc; color:#9b7657; font-size:11px; }.summary-stats b { display:block; margin-top:2px; color:#65432c; font-size:15px; }.summary-log { margin:10px 0 16px; color:#987456; font-size:11px; text-align:left; }.summary-log p { margin:2px 0; }.summary-card > button { width:100%; padding:10px; border:0; border-radius:5px; background:#ca8756; color:#fff; font-size:13px; cursor:pointer; }.summary-card > button:hover { background:#b97649; }.summary-card .summary-close { margin-top:7px; background:transparent; color:#987456; }.summary-card .summary-close:hover { background:#f8ead6; }.summary-enter-active,.summary-leave-active,.task-panel-enter-active,.task-panel-leave-active,.action-panel-enter-active,.action-panel-leave-active { transition:opacity .2s ease,transform .2s ease; }.summary-enter-from,.summary-leave-to,.task-panel-enter-from,.task-panel-leave-to,.action-panel-enter-from,.action-panel-leave-to { opacity:0; transform:translateY(8px); }
@media (max-width:720px) { .game-header { top:max(9px,env(safe-area-inset-top)); left:10px; right:10px; }.icon-button { width:36px; height:36px; font-size:21px; }.header-tools { gap:5px; }.task-button { padding:7px 8px; font-size:11px; }.reset-button { width:34px; height:34px; font-size:18px; }.game-title { min-width:132px; padding:5px 10px 6px; }.game-title h1 { font-size:16px; }.status-strip { top:57px; width:calc(100% - 20px); grid-template-columns:1fr 1fr; gap:6px 9px; padding:7px 9px; }.day-state { grid-column:1/-1; justify-content:center; padding:0 0 5px; border-right:0; border-bottom:1px solid rgba(133,92,52,.14); }.stat { grid-template-columns:27px 1fr 20px; gap:4px; }.room-image { object-position:center; }.action-panel { right:10px; bottom:18px; width:calc(100% - 20px); padding:12px; }.task-panel { top:128px; right:10px; width:calc(100% - 20px); padding:12px; }.result-toast { bottom:12px; font-size:12px; }.room-hotspot span { font-size:10px; padding:1px 4px; }.room-hotspot small { display:none; } }
</style>
