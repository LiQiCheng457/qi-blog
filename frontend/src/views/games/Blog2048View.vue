<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { assetUrl } from '@/utils/assets'

const router = useRouter()

// ── Tile 定义 ─────────────────────────────────────────────────
interface TileDef { img: string; label: string; bg: string; fg: string }

const TILES: Record<number, TileDef> = {
  2:    { img: '/tiles/qi-tile-write.png',  label: '随笔',   bg: 'linear-gradient(135deg,#faf5ed,#f2e8d5)', fg: '#7a6040' },
  4:    { img: '/tiles/qi-tile-code.png',   label: '前端',   bg: 'linear-gradient(135deg,#eef3fa,#d8e8f5)', fg: '#3a5a8a' },
  8:    { img: '/tiles/qi-tile-relax.png',  label: '生活',   bg: 'linear-gradient(135deg,#eef6ee,#d5ecd5)', fg: '#3a7a3a' },
  16:   { img: '/tiles/qi-tile-photo.png',  label: '摄影',   bg: 'linear-gradient(135deg,#faeef6,#f0d8ec)', fg: '#7a3a60' },
  32:   { img: '/tiles/qi-tile-think.png',  label: '折腾',   bg: 'linear-gradient(135deg,#fef6e4,#fce8b8)', fg: '#7a5a20' },
  64:   { img: '/tiles/qi-tile-bath.png',   label: '摸鱼',   bg: 'linear-gradient(135deg,#fdf0e8,#f8dcc8)', fg: '#8a5030' },
  128:  { img: '/tiles/qi-tile-read.png',   label: '泡澡',   bg: 'linear-gradient(135deg,#fde8d0,#f8c8a0)', fg: '#8a4020' },
  256:  { img: '/tiles/qi-tile-cheer.png',  label: '心情',   bg: 'linear-gradient(135deg,#f2eefa,#e2d4f5)', fg: '#5a3a8a' },
  512:  { img: '/tiles/qi-tile-snack.png',  label: '爆款',   bg: 'linear-gradient(135deg,#ff9966,#ff6622)', fg: '#fff' },
  1024: { img: '/tiles/qi-tile-trophy.png', label: '精选',   bg: 'linear-gradient(135deg,#ffcc44,#ffa800)', fg: '#5a3800' },
  2048: { img: '/tiles/qi-tile-wind.png',   label: '起风了', bg: 'linear-gradient(135deg,#ff7c4a,#ff2222)', fg: '#fff' },
}

// ── 2048 核心（转置法）────────────────────────────────────────
type Grid = (number | null)[][]

function emptyGrid(): Grid {
  return Array.from({ length: 4 }, () => Array<number | null>(4).fill(null))
}

function spawnTile(g: Grid): Grid {
  const empties: [number, number][] = []
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) {
    if (g[r][c] === null) empties.push([r, c])
  }
  if (!empties.length) return g
  const [r, c] = empties[Math.floor(Math.random() * empties.length)]
  const ng = g.map(row => [...row]) as Grid
  ng[r][c] = Math.random() < 0.85 ? 2 : 4
  return ng
}

function slideRow(row: (number | null)[]): { row: (number | null)[]; merges: number[] } {
  const nums = row.filter((n): n is number => n !== null)
  const result: (number | null)[] = []
  const merges: number[] = []
  let i = 0
  while (i < nums.length) {
    if (i + 1 < nums.length && nums[i] === nums[i + 1]) {
      const v = nums[i] * 2
      result.push(v); merges.push(v); i += 2
    } else { result.push(nums[i]); i++ }
  }
  while (result.length < 4) result.push(null)
  return { row: result, merges }
}

function reverseRows(g: Grid): Grid { return g.map(row => [...row].reverse()) }

function transpose(g: Grid): Grid {
  const n = g.length
  return Array.from({ length: n }, (_, r) => Array.from({ length: n }, (__, c) => g[c][r]))
}

function applyMove(g: Grid, dir: 'left' | 'right' | 'up' | 'down') {
  let cur = g
  if (dir === 'right') cur = reverseRows(g)
  else if (dir === 'up')   cur = transpose(g)
  else if (dir === 'down') cur = reverseRows(transpose(g))

  const allMerges: number[] = []
  let moved = false
  const slid = cur.map(row => {
    const { row: nr, merges } = slideRow(row)
    allMerges.push(...merges)
    if (JSON.stringify(row) !== JSON.stringify(nr)) moved = true
    return nr
  })

  let result = slid
  if (dir === 'right') result = reverseRows(slid)
  else if (dir === 'up')   result = transpose(slid)
  else if (dir === 'down') result = transpose(reverseRows(slid))
  return { grid: result, merges: allMerges, moved }
}

function isOver(g: Grid): boolean {
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) {
    if (g[r][c] === null) return false
    if (c < 3 && g[r][c] === g[r][c + 1]) return false
    if (r < 3 && g[r][c] === g[r + 1][c]) return false
  }
  return true
}

// ── 状态 ──────────────────────────────────────────────────────
const grid      = ref<Grid>(spawnTile(spawnTile(emptyGrid())))
const gameOver  = ref(false)
const winSeen   = ref(false)
const showWin   = ref(false)
const score     = ref(0)
const bestScore = ref(Number(localStorage.getItem('qi2048_best') ?? '0'))

const qiAvatar  = assetUrl('/animations/qi_wave_small.webp')  // 摆手吉祥物，用于标题 / 弹幕 / 结束遮罩
const qiIcon    = assetUrl('/animations/qi_small.webp')        // 紧凑 logo，用于方块水印 / Tips

function tileDef(val: number) { return TILES[Math.min(val, 2048)] }
function tileStyle(val: number | null) {
  if (!val) return {}
  const def = tileDef(val)
  return def ? { background: def.bg, color: def.fg } : { background: '#aaa', color: '#fff' }
}

function move(dir: 'left' | 'right' | 'up' | 'down') {
  if (gameOver.value) return
  const { grid: ng, merges, moved } = applyMove(grid.value, dir)
  if (!moved) return

  grid.value = spawnTile(ng)

  const gained = merges.reduce((a, v) => a + v, 0)
  score.value += gained
  if (score.value > bestScore.value) {
    bestScore.value = score.value
    localStorage.setItem('qi2048_best', String(score.value))
  }

  if (!winSeen.value && merges.includes(2048)) {
    winSeen.value = true
    showWin.value = true
    setTimeout(() => { showWin.value = false }, 4000)
  }

  if (isOver(grid.value)) gameOver.value = true
}

function restart() {
  grid.value     = spawnTile(spawnTile(emptyGrid()))
  gameOver.value = false
  winSeen.value  = false
  showWin.value  = false
  score.value    = 0
}

const KEY_MAP: Record<string, 'left' | 'right' | 'up' | 'down'> = {
  ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down',
  a: 'left', d: 'right', w: 'up', s: 'down',
}
function onKey(e: KeyboardEvent) {
  const dir = KEY_MAP[e.key]
  if (!dir) return
  e.preventDefault()
  move(dir)
}

let touchOrigin: { x: number; y: number } | null = null
function onTouchStart(e: TouchEvent) {
  const t = e.touches[0]
  touchOrigin = { x: t.clientX, y: t.clientY }
}
function onTouchEnd(e: TouchEvent) {
  if (!touchOrigin) return
  const t = e.changedTouches[0]
  const dx = t.clientX - touchOrigin.x
  const dy = t.clientY - touchOrigin.y
  touchOrigin = null
  if (Math.abs(dx) < 20 && Math.abs(dy) < 20) return
  if (Math.abs(dx) > Math.abs(dy)) move(dx > 0 ? 'right' : 'left')
  else move(dy > 0 ? 'down' : 'up')
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  document.body.classList.add('qi-2048-active')
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  document.body.classList.remove('qi-2048-active')
})
</script>

<template>
  <div class="page" @touchstart.passive="onTouchStart" @touchend="onTouchEnd">

    <!-- 顶部栏 -->
    <header class="top-bar">
      <button class="back-btn" @click="router.push('/games')">← 游戏区</button>
      <div class="score-area">
        <div class="score-box">
          <span class="score-label">分数</span>
          <span class="score-val">{{ score }}</span>
        </div>
        <div class="score-box best">
          <span class="score-label">最佳</span>
          <span class="score-val">{{ bestScore }}</span>
        </div>
      </div>
    </header>

    <!-- 标题区 -->
    <section class="title-section">
      <div class="avatar-wrap">
        <img :src="qiAvatar" class="qi-avatar" alt="水豚祁" />
        <span class="avatar-halo"></span>
      </div>
      <div class="title-text">
        <span class="badge">🎮 益智 · 博客主题</span>
        <h1 class="title">2048 · 起风了版</h1>
        <p class="sub">合并相同格子，凑出「<span class="hl">起风了 🌟</span>」</p>
      </div>
    </section>

    <!-- 通关横幅 -->
    <Transition name="banner">
      <div v-if="showWin" class="win-banner">
        <img :src="qiAvatar" class="banner-qi" alt="" />
        <span>太棒了！水豚祁在为你鼓掌！<br>你合并出了「起风了」🌟 继续挑战更高分～</span>
      </div>
    </Transition>

    <!-- 棋盘 -->
    <div class="board-wrap">
      <div class="board">
        <div v-for="(row, r) in grid" :key="r" class="board-row">
          <div
            v-for="(cell, c) in row"
            :key="c"
            class="cell"
            :class="cell ? 'filled' : 'empty'"
            :style="tileStyle(cell)"
          >
            <template v-if="cell">
              <img :src="assetUrl(tileDef(cell)?.img ?? '')" class="cell-img" :alt="tileDef(cell)?.label ?? ''" draggable="false" />
              <span class="cell-lb">{{ tileDef(cell)?.label ?? cell }}</span>
              <span class="cell-num">{{ cell }}</span>
            </template>
          </div>
        </div>
      </div>

      <!-- 游戏结束遮罩 -->
      <Transition name="board-over">
        <div v-if="gameOver" class="board-over">
          <img :src="qiAvatar" class="over-qi" alt="" />
          <p class="over-title">游戏结束</p>
          <p class="over-score">本局得分 <strong>{{ score }}</strong></p>
          <button class="btn-primary" @click="restart">再来一局</button>
        </div>
      </Transition>
    </div>

    <!-- 操作说明 -->
    <div class="info-row">
      <p class="hint">⌨️ 方向键 / WASD · 📱 手机滑动</p>
      <button class="btn-ghost" @click="restart">🔄 重开</button>
    </div>

    <!-- 水豚祁小Tips -->
    <div class="qi-tips">
      <img :src="qiIcon" class="tips-qi" alt="" />
      <p class="tips-text">
        水豚祁提示：合并到
        <span class="tips-tag"><img :src="assetUrl('/tiles/qi-tile-bath.png')" class="tips-tile-img" alt="" />摸鱼</span> 或
        <span class="tips-tag"><img :src="assetUrl('/tiles/qi-tile-read.png')" class="tips-tile-img" alt="" />泡澡</span>
        才算真正入门～ 目标是
        <span class="tips-tag tips-goal"><img :src="assetUrl('/tiles/qi-tile-wind.png')" class="tips-tile-img" alt="" />起风了</span>！
      </p>
    </div>

  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  max-width: 480px;
  margin: 0 auto;
  padding: 72px 1.25rem 4rem;
  background: var(--qi-bg);
  user-select: none;
  touch-action: none;
}

/* ── 顶部栏 ── */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 0; border-bottom: 1px solid var(--qi-border);
  position: sticky; top: 56px; background: var(--qi-bg); z-index: 10;
}
.back-btn {
  background: none; border: none; font-size: .82rem;
  color: var(--qi-ink-muted); cursor: pointer;
  padding: .3rem .5rem; border-radius: 6px; transition: color .15s;
}
.back-btn:hover { color: var(--qi-primary); }

.score-area { display: flex; gap: .5rem; }
.score-box {
  display: flex; flex-direction: column; align-items: center;
  background: var(--qi-bg-card); border: 1px solid var(--qi-border);
  padding: .35rem .9rem; border-radius: 10px; min-width: 58px;
}
.score-box.best { border-color: rgba(255,140,90,.5); background: rgba(255,140,90,.05); }
.score-label { font-size: .58rem; color: var(--qi-ink-muted); letter-spacing: .08em; text-transform: uppercase; }
.score-val { font-size: 1.1rem; font-weight: 700; color: var(--qi-ink); font-variant-numeric: tabular-nums; line-height: 1.2; }

/* ── 标题 ── */
.title-section {
  display: flex; align-items: center; gap: 1rem;
  padding: 1.375rem 0 1.125rem;
}
.avatar-wrap { position: relative; flex-shrink: 0; width: 68px; height: 68px; }
.qi-avatar { width: 68px; height: 68px; object-fit: contain; position: relative; z-index: 1; }
.avatar-halo {
  position: absolute; inset: -6px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,140,90,.25) 0%, transparent 70%);
  animation: pulse 2.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: .6; transform: scale(1); }
  50%       { opacity: 1;  transform: scale(1.08); }
}

.title-text { min-width: 0; }
.badge {
  display: inline-block; font-size: .66rem; letter-spacing: .06em;
  background: rgba(255,140,90,.12); color: var(--qi-primary);
  padding: .18rem .65rem; border-radius: 999px; margin-bottom: .35rem;
}
.title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.5rem; font-weight: 500; color: var(--qi-ink);
  margin: 0 0 .2rem; line-height: 1.25;
}
.sub { font-size: .78rem; color: var(--qi-ink-muted); margin: 0; }
.hl { color: var(--qi-primary); font-weight: 500; }

/* ── 通关横幅 ── */
.win-banner {
  display: flex; align-items: center; gap: .875rem;
  background: linear-gradient(135deg, #ff8c5a, #ff3333);
  color: #fff; border-radius: 16px;
  padding: 1rem 1.25rem; margin-bottom: 1rem;
  font-size: .82rem; font-weight: 500; line-height: 1.6;
  box-shadow: 0 6px 24px rgba(255,80,60,.3);
}
.banner-qi { width: 40px; height: 40px; object-fit: contain; flex-shrink: 0; }
.banner-enter-active { transition: opacity .3s, transform .3s; }
.banner-leave-active { transition: opacity .3s; }
.banner-enter-from   { opacity: 0; transform: translateY(-10px); }
.banner-leave-to     { opacity: 0; }

/* ── 棋盘 ── */
.board-wrap {
  position: relative;
  background: rgba(200, 180, 155, 0.18);
  border: 1.5px solid var(--qi-border);
  border-radius: 20px; overflow: hidden;
  margin-bottom: .875rem;
  box-shadow: 0 6px 30px rgba(0,0,0,.07), inset 0 1px 0 rgba(255,255,255,.5);
}
.board { display: flex; flex-direction: column; gap: 7px; padding: 7px; }
.board-row { display: flex; gap: 7px; }

.cell {
  flex: 1; aspect-ratio: 1; border-radius: 13px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  transition: transform .06s;
}
.cell.empty {
  background: rgba(200, 185, 165, 0.18);
  box-shadow: inset 0 1px 3px rgba(0,0,0,.06);
}
.cell.filled {
  box-shadow: 0 3px 12px rgba(0,0,0,.12), inset 0 1px 0 rgba(255,255,255,.35);
}

.cell-img {
  width: 72%; height: 72%;
  object-fit: contain;
  position: relative; z-index: 1;
  flex-shrink: 0;
  pointer-events: none;
  border-radius: 6px;
}
.cell-lb {
  font-size: clamp(.48rem, 1.8vw, .68rem);
  font-weight: 600; margin-top: .1rem;
  opacity: .9; position: relative; z-index: 1;
  line-height: 1;
}
.cell-num {
  font-size: clamp(.38rem, 1.3vw, .52rem);
  opacity: .4; margin-top: .05rem;
  font-variant-numeric: tabular-nums;
  position: relative; z-index: 1;
  letter-spacing: -.01em;
}

/* ── 游戏结束遮罩 ── */
.board-over {
  position: absolute; inset: 0;
  background: rgba(255,250,245,.92); backdrop-filter: blur(8px);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: .625rem;
  border-radius: 20px;
}
.over-qi { width: 56px; height: 56px; object-fit: contain; margin-bottom: .25rem; }
.over-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.2rem; color: var(--qi-ink); margin: 0;
}
.over-score { font-size: .85rem; color: var(--qi-ink-muted); margin: 0; }
.over-score strong { color: var(--qi-ink); font-size: 1.1em; }
.board-over-enter-active { transition: opacity .3s; }
.board-over-leave-active { transition: opacity .2s; }
.board-over-enter-from, .board-over-leave-to { opacity: 0; }

/* ── 操作栏 ── */
.info-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1.25rem;
}
.hint { font-size: .7rem; color: var(--qi-ink-light); margin: 0; letter-spacing: .03em; }
.btn-primary {
  padding: .5rem 1.5rem; border-radius: 10px; border: none;
  background: var(--qi-primary); color: #fff;
  font-size: .875rem; font-weight: 500; cursor: pointer; transition: opacity .2s;
}
.btn-primary:hover { opacity: .85; }
.btn-ghost {
  padding: .4rem 1rem; border-radius: 8px;
  border: 1.5px solid var(--qi-border); background: none;
  color: var(--qi-ink-muted); font-size: .8rem;
  cursor: pointer; transition: all .15s;
}
.btn-ghost:hover { border-color: var(--qi-primary); color: var(--qi-primary); }

/* ── 水豚Tips ── */
.qi-tips {
  display: flex; align-items: flex-start; gap: .75rem;
  background: rgba(255,140,90,.06);
  border: 1px solid rgba(255,140,90,.18);
  border-radius: 14px; padding: .875rem 1rem;
}
.tips-qi { width: 32px; height: 32px; object-fit: contain; flex-shrink: 0; margin-top: .1rem; }
.tips-text { font-size: .75rem; color: var(--qi-ink-muted); line-height: 1.7; margin: 0; }
.tips-tag {
  display: inline-flex;
  align-items: center;
  gap: .2rem;
  background: rgba(255,140,90,.12);
  color: var(--qi-primary);
  padding: .05rem .4rem .05rem .2rem;
  border-radius: 6px;
  font-size: .72rem; font-weight: 500;
  vertical-align: middle;
}
.tips-tile-img {
  width: 18px; height: 18px;
  object-fit: contain;
  border-radius: 3px;
  flex-shrink: 0;
}
.tips-tag.tips-goal {
  background: rgba(255,50,50,.1); color: #d93322;
}

:global(body.qi-2048-active) {
  overscroll-behavior: none;
}

@media (max-width: 768px) {
  :global(body.qi-2048-active) {
    overflow: hidden;
    position: fixed;
    inset: 0;
    width: 100%;
  }

  .page {
    width: 100%;
    height: 100dvh;
    max-width: 420px;
    padding: calc(56px + env(safe-area-inset-top)) .75rem calc(.75rem + env(safe-area-inset-bottom));
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .top-bar {
    position: static;
    flex-shrink: 0;
    padding: .45rem 0;
    border-bottom: none;
  }

  .back-btn {
    font-size: .76rem;
    padding: .25rem .35rem;
  }

  .score-area {
    gap: .375rem;
  }

  .score-box {
    min-width: 52px;
    padding: .28rem .55rem;
    border-radius: 8px;
  }

  .score-label {
    font-size: .52rem;
  }

  .score-val {
    font-size: .95rem;
  }

  .title-section {
    flex-shrink: 0;
    gap: .55rem;
    padding: .25rem 0 .5rem;
  }

  .avatar-wrap,
  .qi-avatar {
    width: 42px;
    height: 42px;
  }

  .badge,
  .sub {
    display: none;
  }

  .title {
    font-size: 1.1rem;
    margin: 0;
  }

  .win-banner {
    position: absolute;
    left: .75rem;
    right: .75rem;
    top: calc(104px + env(safe-area-inset-top));
    z-index: 20;
    margin: 0;
    padding: .75rem .875rem;
    border-radius: 12px;
  }

  .board-wrap {
    flex-shrink: 0;
    width: min(100%, calc(100dvh - 210px - env(safe-area-inset-top) - env(safe-area-inset-bottom)));
    margin: 0 auto .6rem;
    border-radius: 16px;
  }

  .board {
    gap: 5px;
    padding: 5px;
  }

  .board-row {
    gap: 5px;
  }

  .cell {
    border-radius: 10px;
  }

  .cell-img {
    width: 68%;
    height: 68%;
  }

  .cell-lb {
    font-size: clamp(.46rem, 2.6vw, .62rem);
  }

  .cell-num {
    font-size: clamp(.34rem, 2vw, .48rem);
  }

  .info-row {
    flex-shrink: 0;
    margin: 0;
    padding-top: .1rem;
  }

  .hint {
    max-width: 62%;
    line-height: 1.35;
    font-size: .64rem;
  }

  .btn-ghost {
    padding: .36rem .8rem;
    font-size: .76rem;
  }

  .qi-tips {
    display: none;
  }
}

@media (max-width: 380px) {
  .title-section {
    padding-bottom: .35rem;
  }

  .avatar-wrap,
  .qi-avatar {
    width: 36px;
    height: 36px;
  }

  .title {
    font-size: 1rem;
  }

  .board-wrap {
    width: min(100%, calc(100dvh - 196px - env(safe-area-inset-top) - env(safe-area-inset-bottom)));
  }
}
</style>
