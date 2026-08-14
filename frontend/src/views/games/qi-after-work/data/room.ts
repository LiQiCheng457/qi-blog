import type { RoomSpotId } from '@/api/room'

export type RoomTool = 'status' | 'collection' | 'memory' | 'emotions' | 'achievements'

export const roomNavigation: Array<{ tool: RoomTool; label: string; icon: string }> = [
  { tool: 'status', label: '房间状态', icon: 'checklist' },
  { tool: 'collection', label: '收藏图鉴', icon: 'memory-box' },
  { tool: 'memory', label: '今日记忆', icon: 'memory-journal' },
  { tool: 'emotions', label: '情绪互动', icon: 'music' },
  { tool: 'achievements', label: '成就', icon: 'achievement-emblem' },
]

export type RoomAction = {
  id: string
  label: string
  detail: string
  result: string
}

export type RoomSpot = {
  id: RoomSpotId
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

export type MoodAction = {
  id: string
  label: string
  spotId: RoomSpotId
  message: string
  emote: string
  effect: string
}

export type ActionOutcome = {
  furniture?: [id: string, state: string]
  collectible?: string
  emote?: string
  effect?: string
}

export const roomAssets = {
  room: '/games/qi-after-work/v2/base/room-day.png',
  qiIdle: '/games/qi-after-work/v2/characters/Qi_Idle.png',
  object: (object: string, state: string) => `/games/qi-after-work/v2/objects/${object}/${state}.png`,
  prop: (name: string) => {
    const [object, ...state] = name.split('-')
    const stateName = state.join('-')
    const resolvedState = object === 'window' && (stateName === 'calm' || stateName === 'rest') ? 'day' : stateName
    return `/games/qi-after-work/v2/objects/${object}/${resolvedState}.png`
  },
  effect: (name: string) => `/games/qi-after-work/v2/effects/${name}.png`,
  collectible: (name: string) => `/games/qi-after-work/v2/collectibles/${name}.png`,
  ui: (name: string) => `/games/qi-after-work/v2/ui/${name}.png`,
  emote: (name: string) => `/games/qi-after-work/v2/characters/qi-${name}.png`,
}

export type RoomSceneObject = {
  id: string
  stateId: string
  defaultState: string
  x: number
  floor: number
  width: number
  z: number
  offsetX?: number
  offsetY?: number
  visible?: boolean
}

export const roomSceneObjects: RoomSceneObject[] = [
  { id: 'window', stateId: 'window', defaultState: 'day', x: 51.5, floor: 46.5, width: 37, z: 2 },
  { id: 'door', stateId: 'door', defaultState: 'closed', x: 24.5, floor: 38.5, width: 13.5, z: 2, offsetY: 5.7 },
  { id: 'fridge', stateId: 'fridge', defaultState: 'closed', x: 35.8, floor: 31.2, width: 15, z: 2, offsetX: -2.4, offsetY: 4.6, visible: false },
  { id: 'sofa', stateId: 'sofa', defaultState: 'idle', x: 51, floor: 28.5, width: 24, z: 2, offsetY: 10.4 },
  { id: 'desk', stateId: 'desk', defaultState: 'off', x: 67.5, floor: 35, width: 16, z: 3, offsetY: 5, visible: false },
  { id: 'console', stateId: 'console', defaultState: 'off', x: 57.5, floor: 38, width: 7.2, z: 4, offsetY: 7.4, visible: false },
  { id: 'bookshelf', stateId: 'bookshelf', defaultState: 'base', x: 79.5, floor: 34, width: 15, z: 2, offsetY: 5.6 },
  { id: 'bed', stateId: 'bed', defaultState: 'made', x: 92, floor: 24, width: 22, z: 2, offsetX: -1, offsetY: 4.3 },
]

export const statusItems = [
  { id: 'desk', label: '书桌', states: ['desk-off', 'desk-working', 'desk-error', 'desk-done'], stateLabels: ['熄屏', '工作中', '出错了', '完成'] },
  { id: 'fridge', label: '冰箱', states: ['fridge-closed', 'fridge-full', 'fridge-empty', 'fridge-fruit'], stateLabels: ['关着', '补满了', '空空的', '有水果'] },
  { id: 'console', label: '游戏机', states: ['console-off', 'console-playing', 'console-win', 'console-lose'], stateLabels: ['关闭', '游戏中', '赢了', '输了'] },
  { id: 'door', label: '门口', states: ['door-closed', 'door-light', 'door-package'], stateLabels: ['关着', '有灯光', '有包裹'] },
  { id: 'bookshelf', label: '书架', states: ['bookshelf-base', 'bookshelf-some', 'bookshelf-full'], stateLabels: ['整齐', '少了一些', '收藏满了'] },
]

export const statusLabels = Object.fromEntries(statusItems.flatMap((item) => item.states.map((state, index) => [state, item.stateLabels[index]]))) as Record<string, string>
export const statusItemLabels = Object.fromEntries(statusItems.map((item) => [item.id, item.label])) as Record<string, string>

export const spotDefaultStates: Record<RoomSpotId, string> = {
  window: 'window-day',
  fridge: 'fridge-closed',
  sofa: 'sofa-idle',
  desk: 'desk-off',
  bookshelf: 'bookshelf-base',
  bed: 'bed-made',
  door: 'door-closed',
}

export const roomStatusLabels: Record<string, string> = {
  ...statusLabels,
  'window-day': '阳光正好',
  'window-rain': '雨声轻轻落下',
  'window-night': '夜色安静',
  'sofa-idle': '柔软又安静',
  'sofa-rest': '正在放松',
  'sofa-music': '音乐时间',
  'bed-made': '整理好了',
  'bed-rest': '适合小憩',
  'bed-sleep': '准备睡觉',
}

export const collectibleItems = [
  ['watermelon', '西瓜切片'], ['strawberry', '草莓'], ['grapes', '紫葡萄'], ['orange', '橙子'], ['star-fruit', '星星水果'],
  ['headphones', '耳机'], ['keyboard', '机械键盘'], ['notepad', '便签本'], ['sleep-pillow', '睡眠枕'], ['backpack', '背包'],
  ['parcel', '神秘包裹'], ['photo', '旧照片'], ['trophy', '小奖杯'], ['mystery-box', '未知盒子'],
] as const

export const achievementItems = [
  { id: 'first-action', title: '第一次互动', detail: '完成一次房间互动', icon: 'trophy' },
  { id: 'first-memory', title: '留下记忆', detail: '在今日记忆中留下记录', icon: 'photo' },
  { id: 'five-collectibles', title: '小小收藏家', detail: '收集 5 件房间物品', icon: 'mystery-box' },
  { id: 'all-collectibles', title: '房间寻宝家', detail: '收集全部房间物品', icon: 'trophy' },
]

export const moodActions: MoodAction[] = [
  { id: 'praise', label: '夸夸祁祁', spotId: 'sofa', message: '我想夸夸你。', emote: 'happy', effect: 'hearts' },
  { id: 'comfort', label: '安慰一下', spotId: 'bed', message: '今天辛苦了，休息一下吧。', emote: 'sleepy', effect: 'sleep' },
  { id: 'thought', label: '在想什么', spotId: 'desk', message: '你现在在想什么？', emote: 'overwhelmed', effect: 'question' },
  { id: 'play', label: '一起玩', spotId: 'desk', message: '要不要一起玩一会儿？', emote: 'happy', effect: 'pixels' },
]

export const spots: RoomSpot[] = [
  { id: 'window', name: '窗边', hint: '看看外面', x: 33, y: 4, width: 37, height: 42, arrivalX: 50, arrivalY: 75, actions: [{ id: 'window-rest', label: '看一会儿天空', detail: '让脑袋安静下来。', result: '窗外的云走得很慢，事情也可以慢一点。' }] },
  { id: 'fridge', name: '冰箱', hint: '找点吃的', x: 30, y: 43, width: 10, height: 30, arrivalX: 38, arrivalY: 77, actions: [{ id: 'fridge-fruit', label: '吃一块水果', detail: '西瓜听起来不错。', result: '冰凉的水果让心情恢复了一点。' }, { id: 'fridge-water', label: '喝杯水', detail: '短暂补充一下。', result: '喝完水，感觉稍微清醒了。' }] },
  { id: 'sofa', name: '沙发', hint: '休息一下', x: 40, y: 38, width: 22, height: 36, arrivalX: 51, arrivalY: 77, actions: [{ id: 'sofa-rest', label: '发一会儿呆', detail: '不做任何事也是安排。', result: '沙发非常理解今天的你。' }, { id: 'sofa-music', label: '听一首歌', detail: '只听一首。', result: '这一首歌正好听完，没有循环到忘记时间。' }] },
  { id: 'desk', name: '书桌', hint: '处理点事情', x: 60.5, y: 42, width: 15, height: 26, arrivalX: 66, arrivalY: 78, actions: [{ id: 'desk-code', label: '看看电脑', detail: '屏幕好像还亮着。', result: '水獭祁盯着屏幕看了一会儿，像是在思考什么。' }, { id: 'desk-note', label: '翻翻桌面便签', detail: '上面可能有没说完的话。', result: '便签上写着：先喝水，再决定要不要继续。' }] },
  { id: 'bookshelf', name: '书架', hint: '翻翻收藏', x: 73, y: 42, width: 11, height: 24, arrivalX: 77, arrivalY: 78, actions: [{ id: 'bookshelf-read', label: '抽出一本书', detail: '不需要读完。', result: '书页里夹着一张旧票根。水獭祁似乎记得那天。' }] },
  { id: 'bed', name: '床', hint: '躺一会儿', x: 82, y: 26, width: 18, height: 48, arrivalX: 88, arrivalY: 78, actions: [{ id: 'bed-nap', label: '坐在床边', detail: '被子看起来很适合躺一下。', result: '水獭祁看了看床，又看了看你，似乎在等一句允许。' }, { id: 'bed-sleep', label: '看看枕头', detail: '也许会发现一场梦的线索。', result: '枕头下藏着一颗小小的水果糖。' }] },
  { id: 'door', name: '门口', hint: '看看有什么动静', x: 18, y: 10, width: 14, height: 54, arrivalX: 27, arrivalY: 77, actions: [{ id: 'door-package', label: '看看门外', detail: '走廊里似乎有一点动静。', result: '门外没有人，只有一阵很轻的风。' }] },
]

export const spotEmotes: Record<RoomSpotId, string> = { window: 'surprised', fridge: 'happy', sofa: 'sleepy', desk: 'overwhelmed', bookshelf: 'surprised', bed: 'sleepy', door: 'surprised' }

export const actionOutcomes: Record<string, ActionOutcome> = {
  'fridge-fruit': { furniture: ['fridge', 'fridge-fruit'], collectible: 'watermelon', emote: 'happy', effect: 'hearts' },
  'fridge-water': { furniture: ['fridge', 'fridge-full'], emote: 'happy', effect: 'rain' },
  'desk-code': { furniture: ['desk', 'desk-working'], emote: 'overwhelmed', effect: 'sweat' },
  'desk-note': { furniture: ['desk', 'desk-done'], collectible: 'notepad', emote: 'happy', effect: 'question' },
  'bookshelf-read': { furniture: ['bookshelf', 'bookshelf-some'], collectible: 'photo', emote: 'surprised', effect: 'surprised' },
  'bed-nap': { furniture: ['bed', 'bed-rest'], collectible: 'sleep-pillow', emote: 'sleepy' },
  'bed-sleep': { furniture: ['bed', 'bed-sleep'], emote: 'sleepy', effect: 'sleep' },
  'door-package': { furniture: ['door', 'door-package'], collectible: 'parcel', emote: 'surprised', effect: 'thundercloud' },
  'sofa-rest': { furniture: ['sofa', 'sofa-rest'], emote: 'sleepy' },
  'sofa-music': { furniture: ['sofa', 'sofa-music'], collectible: 'headphones', emote: 'happy', effect: 'sparkles' },
  'window-rest': { furniture: ['window', 'window-day'], emote: 'surprised', effect: 'sunbeam' },
}
