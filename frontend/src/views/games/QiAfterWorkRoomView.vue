<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { assetUrl } from '@/utils/assets'
import { roomApi, type RoomSpotId } from '@/api/room'
import { useUserStore } from '@/stores/user'

type RoomAction = {
  id: string
  label: string
  detail: string
  result: string
}

type RoomSpot = {
  id: string
  name: string
  hint: string
  x: number
  y: number
  width: number
  height: number
  arrivalX: number
  arrivalY: number
  actions: RoomAction[]
}

const router = useRouter()
const userStore = useUserStore()
const roomImage = assetUrl('/games/qi-after-work/room/Room_Base.png')
const qiIdleImage = assetUrl('/games/qi-after-work/characters/Qi_Idle.png')

const selectedSpotId = ref<string | null>(null)
const lastResult = ref('')
const roomQuestion = ref('')
const roomLoading = ref(false)
const activeEmote = ref<string | null>(null)
const activeEffect = ref<string | null>(null)
const menuOpen = ref(false)
const activeTool = ref<'status' | 'collection' | 'memory' | 'emotions' | 'achievements' | null>(null)
const furnitureStates = ref<Record<string, string>>({})
const discoveredItems = ref<string[]>([])
const memories = ref<{ id: string; title: string; detail: string; createdAt: string }[]>([])
const achievements = ref<string[]>([])
let resultTimer: ReturnType<typeof window.setTimeout> | undefined
let moveTimer: ReturnType<typeof window.setTimeout> | undefined
let emoteTimer: ReturnType<typeof window.setTimeout> | undefined
let effectTimer: ReturnType<typeof window.setTimeout> | undefined
const qiPosition = ref({ x: 50, y: 76 })
const qiMoving = ref(false)
const qiFacingLeft = ref(false)

onMounted(() => {
  document.body.classList.add('qi-after-work-active')
  loadRoomState()
})

onUnmounted(() => {
  document.body.classList.remove('qi-after-work-active')
  if (resultTimer) window.clearTimeout(resultTimer)
  if (moveTimer) window.clearTimeout(moveTimer)
  if (emoteTimer) window.clearTimeout(emoteTimer)
  if (effectTimer) window.clearTimeout(effectTimer)
})

const stateKey = computed(() => `qi-after-work-state:${userStore.profile?.id ?? 'guest'}`)
const stateAsset = (name: string) => assetUrl(`/games/qi-after-work/assets/props/${name}.png`)
const effectAsset = (name: string) => assetUrl(`/games/qi-after-work/assets/effects/${name}.png`)
const collectibleAsset = (name: string) => assetUrl(`/games/qi-after-work/assets/collectibles/${name}.png`)

const statusItems = [
  { id: 'desk', label: '书桌', states: ['desk-off', 'desk-working', 'desk-error', 'desk-done'] },
  { id: 'fridge', label: '冰箱', states: ['fridge-closed', 'fridge-full', 'fridge-empty', 'fridge-fruit'] },
  { id: 'console', label: '游戏机', states: ['console-off', 'console-playing', 'console-win', 'console-lose'] },
  { id: 'door', label: '门口', states: ['door-closed', 'door-light', 'door-package'] },
  { id: 'bookshelf', label: '书架', states: ['bookshelf-base', 'bookshelf-some', 'bookshelf-full'] },
]

const collectibleItems = [
  ['watermelon', '西瓜切片'], ['strawberry', '草莓'], ['grapes', '紫葡萄'], ['orange', '橙子'], ['star-fruit', '星星水果'],
  ['headphones', '耳机'], ['keyboard', '机械键盘'], ['notepad', '便签本'], ['sleep-pillow', '睡眠枕'], ['backpack', '背包'],
  ['parcel', '神秘包裹'], ['photo', '旧照片'], ['trophy', '小奖杯'], ['mystery-box', '未知盒子'],
] as const

const effectImages: Record<string, string> = {
  rain: effectAsset('rain'),
  pixels: effectAsset('game-pixels'),
  hearts: effectAsset('hearts'),
  sparkles: effectAsset('sparkles'),
  sunbeam: effectAsset('sunbeam'),
  question: effectAsset('question'),
  sleep: effectAsset('sleep'),
  surprised: effectAsset('surprised'),
  sweat: effectAsset('sweat'),
  thundercloud: effectAsset('thundercloud'),
}

const moodActions = [
  { id: 'praise', label: '夸夸祁', spotId: 'sofa' as RoomSpotId, message: '我想夸夸你。', emote: 'happy', effect: 'hearts' },
  { id: 'comfort', label: '安慰一下', spotId: 'bed' as RoomSpotId, message: '今天辛苦了，休息一下吧。', emote: 'sleepy', effect: 'sleep' },
  { id: 'thought', label: '在想什么', spotId: 'desk' as RoomSpotId, message: '你现在在想什么？', emote: 'overwhelmed', effect: 'question' },
  { id: 'play', label: '一起玩', spotId: 'desk' as RoomSpotId, message: '要不要一起玩一会儿？', emote: 'happy', effect: 'pixels' },
]

const achievementItems = [
  { id: 'first-action', title: '第一次互动', detail: '完成一次房间互动', icon: 'trophy' },
  { id: 'first-memory', title: '留下记忆', detail: '在今日记忆中留下记录', icon: 'photo' },
  { id: 'five-collectibles', title: '小小收藏家', detail: '收集 5 件房间物品', icon: 'mystery-box' },
  { id: 'all-collectibles', title: '房间寻宝王', detail: '收集全部房间物品', icon: 'trophy' },
]

function loadRoomState() {
  try {
    const saved = JSON.parse(localStorage.getItem(stateKey.value) ?? '{}')
    furnitureStates.value = saved.furnitureStates ?? {}
    discoveredItems.value = saved.discoveredItems ?? []
    memories.value = saved.memories ?? []
    achievements.value = saved.achievements ?? []
  } catch {
    furnitureStates.value = {}
    discoveredItems.value = []
    memories.value = []
    achievements.value = []
  }
}

function saveRoomState() {
  localStorage.setItem(stateKey.value, JSON.stringify({
    furnitureStates: furnitureStates.value,
    discoveredItems: discoveredItems.value,
    memories: memories.value.slice(0, 30),
    achievements: achievements.value,
  }))
}

function unlockItem(id: string) {
  if (!discoveredItems.value.includes(id)) discoveredItems.value.push(id)
  if (discoveredItems.value.length === collectibleItems.length && !achievements.value.includes('all-collectibles')) {
    achievements.value.push('all-collectibles')
  }
}

function addMemory(title: string, detail: string) {
  memories.value.unshift({ id: `${Date.now()}-${Math.random()}`, title, detail, createdAt: new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }) })
  memories.value = memories.value.slice(0, 30)
  if (!achievements.value.includes('first-memory')) achievements.value.push('first-memory')
  saveRoomState()
}

function updateFurniture(id: string, state: string) {
  furnitureStates.value[id] = state
  saveRoomState()
}

function showEffect(name: string) {
  activeEffect.value = effectImages[name] ?? null
  if (effectTimer) window.clearTimeout(effectTimer)
  effectTimer = window.setTimeout(() => { activeEffect.value = null }, 2600)
}

function openTool(tool: typeof activeTool.value) {
  activeTool.value = activeTool.value === tool ? null : tool
  menuOpen.value = true
}

function closeTool() {
  activeTool.value = null
  menuOpen.value = false
}

async function runMoodAction(action: typeof moodActions[number]) {
  activeTool.value = null
  menuOpen.value = false
  showEmote(action.spotId, action.emote)
  showEffect(action.effect)
  addMemory('和水豚祁聊了聊', action.label)
  if (!achievements.value.includes('first-action')) achievements.value.push('first-action')
  saveRoomState()
  await askQi(action.spotId, undefined, action.message)
  resultTimer = window.setTimeout(() => { lastResult.value = '' }, 7200)
}

watch(() => userStore.profile?.id, loadRoomState)

const spots: RoomSpot[] = [
  {
    id: 'window', name: '窗边', hint: '看看外面', x: 1, y: 5, width: 11, height: 48, arrivalX: 13, arrivalY: 75,
    actions: [
      { id: 'window-rest', label: '看一会儿天空', detail: '让脑袋安静下来。', result: '窗外的云走得很慢，事情也可以慢一点。' },
    ],
  },
  {
    id: 'fridge', name: '冰箱', hint: '找点吃的', x: 31, y: 25, width: 10, height: 32, arrivalX: 38, arrivalY: 75,
    actions: [
      { id: 'fridge-fruit', label: '吃一块水果', detail: '西瓜听起来不错。', result: '冰凉的水果让心情恢复了一点。' },
      { id: 'fridge-water', label: '喝杯水', detail: '短暂补充一下。', result: '喝完水，感觉稍微清醒了。' },
    ],
  },
  {
    id: 'sofa', name: '沙发', hint: '休息一下', x: 40, y: 39, width: 17, height: 20, arrivalX: 49, arrivalY: 75,
    actions: [
      { id: 'sofa-rest', label: '发一会儿呆', detail: '不做任何事也是安排。', result: '沙发非常理解今天的你。' },
      { id: 'sofa-music', label: '听一首歌', detail: '只听一首。', result: '这一首歌正好听完，没有循环到忘记时间。' },
    ],
  },
  {
    id: 'desk', name: '书桌', hint: '处理点事情', x: 57, y: 34, width: 15, height: 25, arrivalX: 65, arrivalY: 75,
    actions: [
      { id: 'desk-code', label: '看看电脑', detail: '屏幕好像还亮着。', result: '水豚祁盯着屏幕看了一会儿，像是在思考什么。' },
      { id: 'desk-note', label: '翻翻桌面便签', detail: '上面可能有没说完的话。', result: '便签上写着：先喝水，再决定要不要继续。' },
    ],
  },
  {
    id: 'bookshelf', name: '书架', hint: '翻翻收藏', x: 72, y: 16, width: 9, height: 46, arrivalX: 75, arrivalY: 76,
    actions: [
      { id: 'bookshelf-read', label: '抽出一本书', detail: '不需要读完。', result: '书页里夹着一张旧票根。水豚祁似乎记得那天。' },
    ],
  },
  {
    id: 'bed', name: '床', hint: '躺一下', x: 81, y: 39, width: 18, height: 26, arrivalX: 87, arrivalY: 77,
    actions: [
      { id: 'bed-nap', label: '坐在床边', detail: '被子看起来很适合躺一下。', result: '水豚祁看了看床，又看了看你，似乎在等一句允许。' },
      { id: 'bed-sleep', label: '看看枕头', detail: '也许会发现一场梦的线索。', result: '枕头下藏着一颗小小的水果糖。' },
    ],
  },
  {
    id: 'door', name: '门口', hint: '看看有什么动静', x: 17, y: 17, width: 10, height: 39, arrivalX: 26, arrivalY: 75,
    actions: [
      { id: 'door-package', label: '看看门外', detail: '走廊里似乎有一点动静。', result: '门外没有人，只有一阵很轻的风。' },
    ],
  },
]

const selectedSpot = computed(() => spots.find((spot) => spot.id === selectedSpotId.value) ?? null)
const bubbleOnLeft = computed(() => qiPosition.value.x > 62)
const bubbleStyle = computed(() => ({
  left: `${qiPosition.value.x}%`,
  top: `calc(${qiPosition.value.y}% - clamp(150px, 16vw, 270px))`,
}))

const emoteImages: Record<string, string> = {
  surprised: assetUrl('/games/qi-after-work/assets/emotes/qi-surprised.png'),
  happy: assetUrl('/games/qi-after-work/assets/emotes/qi-happy.png'),
  sleepy: assetUrl('/games/qi-after-work/assets/emotes/qi-sleepy.png'),
  overwhelmed: assetUrl('/games/qi-after-work/assets/emotes/qi-overwhelmed.png'),
}

const spotEmotes: Record<RoomSpotId, string> = {
  window: 'surprised',
  fridge: 'happy',
  sofa: 'sleepy',
  desk: 'overwhelmed',
  bookshelf: 'surprised',
  bed: 'sleepy',
  door: 'surprised',
}

function showEmote(spotId: RoomSpotId, emote = spotEmotes[spotId]) {
  activeEmote.value = emoteImages[emote] ?? emoteImages.surprised
  if (emoteTimer) window.clearTimeout(emoteTimer)
  emoteTimer = window.setTimeout(() => { activeEmote.value = null }, 3000)
}

function moveQi(x: number, y: number, onArrive?: () => void) {
  if (moveTimer) window.clearTimeout(moveTimer)
  const distance = Math.abs(x - qiPosition.value.x) + Math.abs(y - qiPosition.value.y)
  qiFacingLeft.value = x < qiPosition.value.x
  qiMoving.value = true
  qiPosition.value = { x, y }
  const duration = Math.min(2800, Math.max(900, distance * 65))
  moveTimer = window.setTimeout(() => {
    qiMoving.value = false
    onArrive?.()
  }, duration)
}

function selectSpot(id: string) {
  const spot = spots.find((item) => item.id === id)
  if (!spot) return
  selectedSpotId.value = null
  lastResult.value = ''
  moveQi(spot.arrivalX, spot.arrivalY, () => {
    selectedSpotId.value = id
    showEmote(id as RoomSpotId)
  })
}

function walkToFloor(event: MouseEvent) {
  if ((event.target as HTMLElement).closest('.room-hotspot, .action-panel, .room-menu, .room-tool-panel, .game-header')) return
  const stage = event.currentTarget as HTMLElement
  const rect = stage.getBoundingClientRect()
  const x = Math.max(7, Math.min(93, ((event.clientX - rect.left) / rect.width) * 100))
  const y = Math.max(67, Math.min(91, ((event.clientY - rect.top) / rect.height) * 100))
  selectedSpotId.value = null
  lastResult.value = ''
  moveQi(x, y)
}

async function askQi(spotId: RoomSpotId, actionId?: string, message = '') {
  if (!userStore.isLoggedIn) {
    lastResult.value = '水豚祁歪了歪头：先登录，再慢慢聊吧。'
    return
  }

  roomLoading.value = true
  lastResult.value = '…'
  showEmote(spotId)
  try {
    let receivedFirstChunk = false
    await roomApi.chatStream({ spotId, actionId, message }, (chunk) => {
      if (!receivedFirstChunk) {
        lastResult.value = ''
        receivedFirstChunk = true
      }
      lastResult.value += chunk
    })
  } catch (error) {
    lastResult.value = error instanceof Error ? error.message : '水豚祁现在没有接上信号，请稍后再试。'
  } finally {
    roomLoading.value = false
  }
}

async function runAction(action: RoomAction) {
  const spotId = selectedSpot.value?.id as RoomSpotId | undefined
  if (!spotId) return
  lastResult.value = action.result
  const stateMap: Record<string, [string, string, string?, string?]> = {
    'fridge-fruit': ['fridge', 'fridge-fruit', 'watermelon', 'happy'],
    'fridge-water': ['fridge', 'fridge-full', undefined, 'happy'],
    'desk-code': ['desk', 'desk-working', undefined, 'overwhelmed'],
    'desk-note': ['desk', 'desk-done', 'notepad', 'happy'],
    'bookshelf-read': ['bookshelf', 'bookshelf-some', 'photo', 'surprised'],
    'bed-nap': ['bed', 'bed-rest', 'sleep-pillow', 'sleepy'],
    'bed-sleep': ['bed', 'bed-sleep', undefined, 'sleepy'],
    'door-package': ['door', 'door-package', 'parcel', 'surprised'],
    'sofa-rest': ['sofa', 'sofa-rest', undefined, 'sleepy'],
    'sofa-music': ['sofa', 'sofa-music', 'headphones', 'happy'],
    'window-rest': ['window', 'window-rest', undefined, 'surprised'],
  }
  const [stateId, state, collectible, emote] = stateMap[action.id] ?? []
  if (stateId && state) updateFurniture(stateId, state)
  if (collectible) unlockItem(collectible)
  if (emote) showEmote(spotId, emote)
  const actionEffects: Record<string, string> = {
    'fridge-fruit': 'hearts',
    'fridge-water': 'rain',
    'sofa-music': 'sparkles',
    'desk-code': 'sweat',
    'desk-note': 'question',
    'bookshelf-read': 'surprised',
    'bed-sleep': 'sleep',
    'window-rest': 'sunbeam',
    'door-package': 'thundercloud',
  }
  if (actionEffects[action.id]) showEffect(actionEffects[action.id])
  addMemory(selectedSpot.value?.name ?? '房间', action.label)
  if (!achievements.value.includes('first-action')) achievements.value.push('first-action')
  if (discoveredItems.value.length >= 5 && !achievements.value.includes('five-collectibles')) achievements.value.push('five-collectibles')
  saveRoomState()
  if (resultTimer) window.clearTimeout(resultTimer)
  selectedSpotId.value = null
  await askQi(spotId, action.id)
  resultTimer = window.setTimeout(() => { lastResult.value = '' }, 5200)
}

async function askFromRoom() {
  const spotId = selectedSpot.value?.id as RoomSpotId | undefined
  const message = roomQuestion.value.trim()
  if (!spotId || !message || roomLoading.value) return
  roomQuestion.value = ''
  selectedSpotId.value = null
  await askQi(spotId, undefined, message)
  resultTimer = window.setTimeout(() => { lastResult.value = '' }, 7200)
}
</script>

<template>
  <div class="after-work-page">
    <header class="game-header">
      <button class="icon-button" type="button" title="返回游戏区" aria-label="返回游戏区" @click="router.push('/games')">←</button>
      <div class="room-tools">
        <button class="icon-button" type="button" title="房间菜单" aria-label="房间菜单" @click="menuOpen = !menuOpen">☰</button>
        <aside v-if="menuOpen" class="room-menu" aria-label="房间功能菜单">
          <button type="button" :class="{ active: activeTool === 'status' }" @click="openTool('status')">房间状态</button>
          <button type="button" :class="{ active: activeTool === 'collection' }" @click="openTool('collection')">收藏图鉴</button>
          <button type="button" :class="{ active: activeTool === 'memory' }" @click="openTool('memory')">今日记忆</button>
          <button type="button" :class="{ active: activeTool === 'emotions' }" @click="openTool('emotions')">情绪互动</button>
          <button type="button" :class="{ active: activeTool === 'achievements' }" @click="openTool('achievements')">成就</button>
        </aside>
      </div>
    </header>

    <main class="room-shell">
      <div class="room-stage" @click="walkToFloor">
        <img :src="roomImage" class="room-image" alt="水豚祁的房间" draggable="false" />
        <div class="sun-wash"></div>

        <div
          class="qi-character"
          :class="{ moving: qiMoving, 'facing-left': qiFacingLeft }"
          :style="{ left: `${qiPosition.x}%`, top: `${qiPosition.y}%` }"
          aria-label="水豚祁"
        >
          <img :src="qiIdleImage" alt="水豚祁" draggable="false" />
          <span v-if="qiMoving">走走…</span>
        </div>

        <Transition name="qi-emote">
          <img
            v-if="activeEmote && !selectedSpot"
            class="qi-emote"
            :src="activeEmote"
            alt=""
            aria-hidden="true"
            :style="{ left: `${qiPosition.x}%`, top: `calc(${qiPosition.y}% - clamp(100px, 11vw, 180px))` }"
          />
        </Transition>

        <Transition name="room-effect">
          <img
            v-if="activeEffect"
            :src="activeEffect"
            class="room-effect"
            alt=""
            aria-hidden="true"
            :style="{ left: `${qiPosition.x}%`, top: `calc(${qiPosition.y}% - clamp(150px, 16vw, 250px))` }"
          />
        </Transition>

        <Transition name="qi-bubble">
          <aside
            v-if="lastResult && !selectedSpot"
            class="qi-dialogue"
            :class="{ 'qi-dialogue--left': bubbleOnLeft }"
            :style="bubbleStyle"
            aria-live="polite"
          >
            <p>{{ lastResult }}</p>
          </aside>
        </Transition>

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
            <form class="room-question" @submit.prevent="askFromRoom">
              <input v-model="roomQuestion" :disabled="roomLoading" maxlength="200" placeholder="问问水豚祁…" aria-label="向水豚祁提问" />
              <button type="submit" :disabled="roomLoading || !roomQuestion.trim()">{{ roomLoading ? '…' : '问' }}</button>
            </form>
          </aside>
        </Transition>

        <Transition name="tool-panel">
          <aside v-if="activeTool" class="room-tool-panel" aria-live="polite">
            <div class="tool-heading">
              <h2>{{ activeTool === 'status' ? '房间状态' : activeTool === 'collection' ? '收藏图鉴' : activeTool === 'memory' ? '今日记忆' : activeTool === 'emotions' ? '情绪互动' : '成就' }}</h2>
              <button type="button" aria-label="关闭菜单" @click="closeTool">×</button>
            </div>

            <div v-if="activeTool === 'status'" class="status-grid">
              <article v-for="item in statusItems" :key="item.id" class="status-card">
                <img :src="stateAsset(furnitureStates[item.id] ?? item.states[0])" :alt="item.label" />
                <div><strong>{{ item.label }}</strong><small>当前状态</small></div>
                <div class="state-options">
                  <button v-for="state in item.states" :key="state" type="button" :class="{ active: (furnitureStates[item.id] ?? item.states[0]) === state }" :title="state" @click="updateFurniture(item.id, state)"></button>
                </div>
              </article>
            </div>

            <div v-else-if="activeTool === 'collection'">
              <p class="collection-progress">已收集 {{ discoveredItems.length }} / {{ collectibleItems.length }}</p>
              <div class="collection-grid">
                <article v-for="item in collectibleItems" :key="item[0]" class="collection-item" :class="{ locked: !discoveredItems.includes(item[0]) }">
                  <img :src="collectibleAsset(item[0])" :alt="discoveredItems.includes(item[0]) ? item[1] : '未知收藏'" />
                  <span>{{ discoveredItems.includes(item[0]) ? item[1] : '未知收藏' }}</span>
                </article>
              </div>
            </div>

            <div v-else-if="activeTool === 'memory'" class="memory-list">
              <p v-if="!memories.length" class="tool-empty">房间还没有新记忆。</p>
              <article v-for="memory in memories" :key="memory.id" class="memory-item">
                <time>{{ memory.createdAt }}</time><strong>{{ memory.title }}</strong><p>{{ memory.detail }}</p>
              </article>
            </div>

            <div v-else-if="activeTool === 'emotions'" class="mood-grid">
              <button v-for="action in moodActions" :key="action.id" class="mood-button" type="button" :disabled="roomLoading" @click="runMoodAction(action)">{{ action.label }}</button>
            </div>

            <div v-else class="achievement-list">
              <article v-for="achievement in achievementItems" :key="achievement.id" class="achievement-item" :class="{ locked: !achievements.includes(achievement.id) }">
                <img :src="collectibleAsset(achievement.icon)" alt="" /><div><strong>{{ achievement.title }}</strong><span>{{ achievement.detail }}</span></div>
              </article>
            </div>
          </aside>
        </Transition>

      </div>
    </main>
  </div>
</template>

<style scoped>
:global(body.qi-after-work-active),:global(body.qi-after-work-active #app),:global(body.qi-after-work-active main) { height:100dvh; overflow:hidden; }
.after-work-page { position:relative; width:100%; height:100dvh; overflow:hidden; background:#ecbd7c; color:#5c422b; isolation:isolate; }
.game-header { position:absolute; z-index:5; top:max(14px,env(safe-area-inset-top)); left:16px; right:16px; display:flex; align-items:center; justify-content:space-between; pointer-events:none; }
.room-shell { position:absolute; inset:0; z-index:0; }.room-stage { position:relative; width:100%; height:100%; overflow:hidden; background:#f4ddb9; isolation:isolate; }.room-image { display:block; width:100%; height:100%; object-fit:cover; object-position:center; user-select:none; }.sun-wash { position:absolute; inset:0; z-index:1; pointer-events:none; background:rgba(255,240,196,.03); }
.qi-character { position:absolute; z-index:3; width:clamp(80px,7vw,135px); transform:translate(-50%,-100%); transition:left 1.35s cubic-bezier(.22,.78,.32,1),top 1.35s cubic-bezier(.22,.78,.32,1); pointer-events:none; filter:drop-shadow(0 6px 6px rgba(83,55,26,.2)); }.qi-character img { display:block; width:100%; height:auto; animation:qi-idle 2.6s ease-in-out infinite; transform-origin:center bottom; user-select:none; }.qi-character.facing-left img { transform:scaleX(-1); }.qi-character.moving img { animation:qi-walk .42s ease-in-out infinite alternate; }.qi-character span { position:absolute; top:-10px; left:50%; padding:2px 6px; transform:translateX(-50%); border-radius:4px; background:rgba(255,250,240,.86); color:#806046; font-size:10px; white-space:nowrap; }.qi-emote { position:absolute; z-index:4; width:clamp(72px,8vw,125px); transform:translate(-50%,-100%); pointer-events:none; filter:drop-shadow(0 5px 6px rgba(83,55,26,.13)); }.room-hotspot { position:absolute; z-index:2; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:0; border:0; outline:0; background:transparent; color:#6b4630; cursor:pointer; }.room-hotspot span,.room-hotspot small { opacity:0; pointer-events:none; transition:opacity .16s ease,transform .16s ease; }.room-hotspot span { padding:2px 7px; border-radius:4px; background:rgba(255,251,241,.94); box-shadow:0 2px 8px rgba(92,58,29,.12); font-size:12px; font-weight:700; transform:translateY(3px); }.room-hotspot small { margin-top:3px; font-size:10px; color:#8a684d; }.room-hotspot:hover span,.room-hotspot:hover small,.room-hotspot:focus-visible span,.room-hotspot:focus-visible small { opacity:1; }.room-hotspot:hover span,.room-hotspot:focus-visible span { transform:translateY(0); }.room-hotspot:focus-visible { box-shadow:inset 0 0 0 2px rgba(255,250,235,.86); border-radius:4px; }
.icon-button { pointer-events:auto; display:grid; width:40px; height:40px; place-items:center; border:1px solid rgba(255,249,234,.54); border-radius:50%; background:rgba(97,65,36,.28); box-shadow:0 4px 14px rgba(86,52,24,.16); color:#fffaf0; font-size:23px; line-height:1; backdrop-filter:blur(7px); cursor:pointer; }.icon-button:hover { background:rgba(97,65,36,.45); }
.room-tools { position:relative; pointer-events:auto; }.room-menu { position:absolute; top:48px; right:0; z-index:12; display:grid; width:126px; padding:5px; border:1px solid rgba(255,249,234,.62); border-radius:7px; background:rgba(255,250,240,.95); box-shadow:0 12px 28px rgba(84,54,29,.2); backdrop-filter:blur(10px); }.room-menu button { padding:8px 9px; border:0; border-radius:4px; background:transparent; color:#694a34; font:12px inherit; text-align:left; cursor:pointer; }.room-menu button:hover,.room-menu button.active { background:#ffead0; color:#9a5f39; }
.action-panel { position:absolute; z-index:6; right:20px; bottom:22px; width:min(330px,calc(100% - 40px)); padding:15px; border:1px solid rgba(255,249,234,.55); border-radius:7px; background:rgba(255,250,240,.94); box-shadow:0 15px 36px rgba(84,54,29,.23); backdrop-filter:blur(10px); }.panel-heading { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; }.panel-heading span { font-size:11px; color:#ab805c; }.panel-heading h2 { margin:1px 0 0; font:600 19px/1.2 'Noto Serif SC',serif; }.panel-heading button { border:0; background:transparent; color:#987252; font-size:21px; line-height:1; cursor:pointer; }.action-button { display:block; width:100%; margin-top:7px; padding:10px 11px; border:1px solid rgba(152,104,61,.18); border-radius:5px; background:#fff6e8; color:#684631; text-align:left; cursor:pointer; }.action-button:hover { background:#ffebd2; border-color:rgba(178,108,58,.45); }.action-button strong,.action-button span { display:block; }.action-button strong { font-size:13px; }.action-button span { margin-top:2px; font-size:11px; color:#987456; }.room-question { display:flex; gap:6px; margin-top:11px; padding-top:11px; border-top:1px solid rgba(152,104,61,.14); }.room-question input { min-width:0; flex:1; border:1px solid rgba(152,104,61,.25); border-radius:5px; outline:0; background:#fffdf7; color:#684631; padding:8px 9px; font:12px inherit; }.room-question input:focus { border-color:#c98c5f; }.room-question button { width:36px; border:0; border-radius:5px; background:#c98c5f; color:#fff; cursor:pointer; }.room-question button:disabled { opacity:.5; cursor:default; }
.qi-dialogue { position:absolute; z-index:5; width:fit-content; max-width:min(310px,34vw); margin-left:clamp(26px,3vw,48px); padding:12px 14px; border:1px solid rgba(152,104,61,.25); border-radius:7px; background:rgba(255,250,240,.94); box-shadow:0 8px 22px rgba(85,52,25,.16); color:#6f4e36; font-size:13px; line-height:1.65; backdrop-filter:blur(7px); pointer-events:none; }.qi-dialogue::after { content:''; position:absolute; bottom:-8px; left:18px; width:14px; height:14px; border-right:1px solid rgba(152,104,61,.25); border-bottom:1px solid rgba(152,104,61,.25); background:rgba(255,250,240,.94); transform:rotate(45deg); }.qi-dialogue--left { margin:0 clamp(26px,3vw,48px) 0 0; transform:translateX(-100%); }.qi-dialogue--left::after { right:18px; left:auto; border:0; border-left:1px solid rgba(152,104,61,.25); border-bottom:1px solid rgba(152,104,61,.25); }.qi-dialogue p { margin:0; }.qi-bubble-enter-active,.qi-bubble-leave-active { transition:opacity .2s ease,transform .2s ease; }.qi-bubble-enter-from,.qi-bubble-leave-to { opacity:0; transform:translateY(8px); }
.room-effect { position:absolute; z-index:4; width:clamp(84px,11vw,170px); transform:translate(-50%,-100%); pointer-events:none; filter:drop-shadow(0 4px 7px rgba(83,55,26,.16)); }.room-effect-enter-active,.room-effect-leave-active { transition:opacity .35s ease,transform .35s ease; }.room-effect-enter-from,.room-effect-leave-to { opacity:0; transform:translate(-50%,-85%) scale(.78); }
.room-tool-panel { position:absolute; z-index:11; top:64px; right:20px; width:min(370px,calc(100% - 40px)); max-height:calc(100% - 86px); overflow:auto; padding:14px; border:1px solid rgba(255,249,234,.62); border-radius:7px; background:rgba(255,250,240,.96); box-shadow:0 15px 36px rgba(84,54,29,.23); backdrop-filter:blur(11px); }.tool-heading { display:flex; align-items:center; justify-content:space-between; margin-bottom:11px; border-bottom:1px solid rgba(152,104,61,.14); padding-bottom:9px; }.tool-heading h2 { margin:0; color:#65452f; font:600 18px/1.2 'Noto Serif SC',serif; }.tool-heading button { display:grid; width:27px; height:27px; place-items:center; border:0; border-radius:4px; background:transparent; color:#987252; font-size:22px; cursor:pointer; }.tool-heading button:hover { background:#ffead0; }.status-grid { display:grid; gap:8px; }.status-card { display:grid; grid-template-columns:64px 1fr; align-items:center; gap:9px; padding:7px; border-bottom:1px solid rgba(152,104,61,.12); }.status-card img { width:64px; height:49px; object-fit:contain; }.status-card strong,.status-card small { display:block; }.status-card strong { font-size:13px; }.status-card small { margin-top:2px; color:#987456; font-size:11px; }.state-options { grid-column:1 / -1; display:flex; gap:5px; }.state-options button { width:20px; height:5px; border:0; border-radius:3px; background:#e6c2a1; cursor:pointer; }.state-options button.active,.state-options button:hover { background:#bc7547; }.collection-progress { margin:0 0 10px; color:#8a6044; font-size:12px; }.collection-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:7px; }.collection-item { min-width:0; padding:5px 3px; border:1px solid rgba(152,104,61,.13); border-radius:5px; text-align:center; }.collection-item img { display:block; width:100%; height:52px; object-fit:contain; }.collection-item span { display:block; overflow:hidden; margin-top:3px; color:#744f37; font-size:10px; text-overflow:ellipsis; white-space:nowrap; }.collection-item.locked img { filter:grayscale(1) brightness(.52); }.collection-item.locked span { color:#a98b74; }.memory-list,.achievement-list { display:grid; gap:8px; }.tool-empty { margin:4px 0; color:#9a755a; font-size:12px; }.memory-item { padding:9px; border-left:3px solid #d69b6d; background:#fff6e8; }.memory-item time { display:block; margin-bottom:2px; color:#a77a5b; font-size:10px; }.memory-item strong { color:#674630; font-size:13px; }.memory-item p { margin:3px 0 0; color:#8e694f; font-size:12px; }.mood-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:8px; }.mood-button { min-height:52px; border:1px solid rgba(152,104,61,.18); border-radius:5px; background:#fff6e8; color:#694a34; font:13px inherit; cursor:pointer; }.mood-button:hover { background:#ffead0; border-color:rgba(178,108,58,.45); }.mood-button:disabled { opacity:.55; cursor:default; }.achievement-item { display:flex; align-items:center; gap:10px; padding:8px; border:1px solid rgba(152,104,61,.13); border-radius:5px; }.achievement-item img { width:42px; height:42px; object-fit:contain; }.achievement-item strong,.achievement-item span { display:block; }.achievement-item strong { color:#694a34; font-size:13px; }.achievement-item span { margin-top:2px; color:#987456; font-size:11px; }.achievement-item.locked { opacity:.52; filter:grayscale(1); }.tool-panel-enter-active,.tool-panel-leave-active { transition:opacity .2s ease,transform .2s ease; }.tool-panel-enter-from,.tool-panel-leave-to { opacity:0; transform:translateY(-6px); }
.action-panel-enter-active,.action-panel-leave-active,.qi-emote-enter-active,.qi-emote-leave-active { transition:opacity .22s ease,transform .22s ease; }.action-panel-enter-from,.action-panel-leave-to { opacity:0; transform:translateY(8px); }.qi-emote-enter-from,.qi-emote-leave-to { opacity:0; transform:translate(-50%,-100%) scale(.72) rotate(-8deg); }@keyframes qi-idle { from { translate:0 0; } 50% { translate:0 -3px; } to { translate:0 0; } }@keyframes qi-walk { from { translate:0 0; rotate:-2deg; } to { translate:0 -5px; rotate:2deg; } }
@media (max-width:720px) { .game-header { top:max(9px,env(safe-area-inset-top)); left:10px; right:10px; }.icon-button { width:36px; height:36px; font-size:21px; }.room-image { object-position:center; }.action-panel { right:10px; bottom:18px; width:calc(100% - 20px); padding:12px; }.qi-dialogue { width:min(245px,61vw); margin-left:18px; padding:10px 11px; font-size:12px; }.qi-dialogue--left { margin-right:18px; }.room-hotspot span { font-size:10px; padding:1px 4px; }.room-hotspot small { display:none; } }
</style>
