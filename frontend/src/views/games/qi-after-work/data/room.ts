import type { RoomSpotId } from '@/api/room'

export type RoomTool = 'status' | 'collection' | 'memory' | 'emotions' | 'achievements'

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
  room: '/games/qi-after-work/room/Room_Base.png',
  qiIdle: '/games/qi-after-work/characters/Qi_Idle.png',
  prop: (name: string) => `/games/qi-after-work/assets/props/${name}.png`,
  effect: (name: string) => `/games/qi-after-work/assets/effects/${name}.png`,
  collectible: (name: string) => `/games/qi-after-work/assets/collectibles/${name}.png`,
  emote: (name: string) => `/games/qi-after-work/assets/emotes/qi-${name}.png`,
}

export const statusItems = [
  { id: 'desk', label: '书桌', states: ['desk-off', 'desk-working', 'desk-error', 'desk-done'], stateLabels: ['熄屏', '工作中', '出错了', '完成'] },
  { id: 'fridge', label: '冰箱', states: ['fridge-closed', 'fridge-full', 'fridge-empty', 'fridge-fruit'], stateLabels: ['关着', '补满了', '空空的', '有水果'] },
  { id: 'console', label: '游戏机', states: ['console-off', 'console-playing', 'console-win', 'console-lose'], stateLabels: ['关闭', '游戏中', '赢了', '输了'] },
  { id: 'door', label: '门口', states: ['door-closed', 'door-light', 'door-package'], stateLabels: ['关着', '有灯光', '有包裹'] },
  { id: 'bookshelf', label: '书架', states: ['bookshelf-base', 'bookshelf-some', 'bookshelf-full'], stateLabels: ['整齐', '少了一些', '收藏满了'] },
]

export const statusPositions: Record<string, { x: number; y: number }> = {
  window: { x: 9, y: 48 },
  fridge: { x: 35, y: 43 },
  console: { x: 66, y: 43 },
  desk: { x: 64, y: 56 },
  door: { x: 22, y: 48 },
  bookshelf: { x: 76, y: 45 },
}

export const statusLabels = Object.fromEntries(statusItems.flatMap((item) => item.states.map((state, index) => [state, item.stateLabels[index]]))) as Record<string, string>
export const statusItemLabels = Object.fromEntries(statusItems.map((item) => [item.id, item.label])) as Record<string, string>

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
  { id: 'window', name: '窗边', hint: '看看外面', x: 1, y: 5, width: 11, height: 48, arrivalX: 13, arrivalY: 75, actions: [{ id: 'window-rest', label: '看一会儿天空', detail: '让脑袋安静下来。', result: '窗外的云走得很慢，事情也可以慢一点。' }] },
  { id: 'fridge', name: '冰箱', hint: '找点吃的', x: 31, y: 25, width: 10, height: 32, arrivalX: 38, arrivalY: 75, actions: [{ id: 'fridge-fruit', label: '吃一块水果', detail: '西瓜听起来不错。', result: '冰凉的水果让心情恢复了一点。' }, { id: 'fridge-water', label: '喝杯水', detail: '短暂补充一下。', result: '喝完水，感觉稍微清醒了。' }] },
  { id: 'sofa', name: '沙发', hint: '休息一下', x: 40, y: 39, width: 17, height: 20, arrivalX: 49, arrivalY: 75, actions: [{ id: 'sofa-rest', label: '发一会儿呆', detail: '不做任何事也是安排。', result: '沙发非常理解今天的你。' }, { id: 'sofa-music', label: '听一首歌', detail: '只听一首。', result: '这一首歌正好听完，没有循环到忘记时间。' }] },
  { id: 'desk', name: '书桌', hint: '处理点事情', x: 57, y: 34, width: 15, height: 25, arrivalX: 65, arrivalY: 75, actions: [{ id: 'desk-code', label: '看看电脑', detail: '屏幕好像还亮着。', result: '水獭祁盯着屏幕看了一会儿，像是在思考什么。' }, { id: 'desk-note', label: '翻翻桌面便签', detail: '上面可能有没说完的话。', result: '便签上写着：先喝水，再决定要不要继续。' }] },
  { id: 'bookshelf', name: '书架', hint: '翻翻收藏', x: 72, y: 16, width: 9, height: 46, arrivalX: 75, arrivalY: 76, actions: [{ id: 'bookshelf-read', label: '抽出一本书', detail: '不需要读完。', result: '书页里夹着一张旧票根。水獭祁似乎记得那天。' }] },
  { id: 'bed', name: '床', hint: '躺一会儿', x: 81, y: 39, width: 18, height: 26, arrivalX: 87, arrivalY: 77, actions: [{ id: 'bed-nap', label: '坐在床边', detail: '被子看起来很适合躺一下。', result: '水獭祁看了看床，又看了看你，似乎在等一句允许。' }, { id: 'bed-sleep', label: '看看枕头', detail: '也许会发现一场梦的线索。', result: '枕头下藏着一颗小小的水果糖。' }] },
  { id: 'door', name: '门口', hint: '看看有什么动静', x: 17, y: 17, width: 10, height: 39, arrivalX: 26, arrivalY: 75, actions: [{ id: 'door-package', label: '看看门外', detail: '走廊里似乎有一点动静。', result: '门外没有人，只有一阵很轻的风。' }] },
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
  'window-rest': { furniture: ['window', 'window-rest'], emote: 'surprised', effect: 'sunbeam' },
}
