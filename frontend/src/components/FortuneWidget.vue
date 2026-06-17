<script setup lang="ts">
import { ref, computed } from 'vue'
import html2canvas from 'html2canvas'

// ── 种子随机（同一天所有人结果相同）────────────────────────────────────
function seedRng(seed: number) {
  let s = seed
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff
    return (s >>> 0) / 0xffffffff
  }
}
function dateSeed(): number {
  const d = new Date()
  return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate()
}
function pick<T>(rng: () => number, arr: T[]): T {
  return arr[Math.floor(rng() * arr.length)]
}
function pickN<T>(rng: () => number, arr: T[], n: number): T[] {
  const shuffled = [...arr].sort(() => rng() - 0.5)
  return shuffled.slice(0, n)
}

// ── 词库 ─────────────────────────────────────────────────────────────
const FORTUNES = [
  { yi: '摸鱼', ji: '重构' },
  { yi: '喝奶茶', ji: '看体重秤' },
  { yi: '摆烂', ji: '立 Flag' },
  { yi: '午睡', ji: '开会' },
  { yi: '发呆', ji: '看需求文档' },
  { yi: '躺平', ji: '加班' },
  { yi: '聊天', ji: '写文档' },
  { yi: '刷视频', ji: '背单词' },
  { yi: '囤外卖优惠券', ji: '减肥' },
  { yi: '打游戏', ji: '早睡' },
  { yi: '网购', ji: '看账单' },
  { yi: '叫外卖', ji: '自己做饭' },
  { yi: '云旅游', ji: '真出门' },
  { yi: '做白日梦', ji: '认清现实' },
]

const OVERALL_LEVELS = [
  { score: 8, label: '运势大凶', desc: '今天建议全程躺平，任何主动行为都有风险，包括起床。' },
  { score: 25, label: '小有波折', desc: '运势偏弱，建议减少决策，把今天的事推到明天再说。' },
  { score: 42, label: '平平无奇', desc: '就那样吧，既不会中彩票，也不会被流星砸到，普通的一天。' },
  { score: 61, label: '尚可一战', desc: '运势中等偏上，适合做一些低风险的事，比如订外卖。' },
  { score: 78, label: '顺风顺水', desc: '今天气场不错，但也别膨胀，毕竟明天还不确定。' },
  { score: 91, label: '鸿运当头', desc: '运势极佳，但你可能只会用来多睡了半小时。' },
]

const LUCKY_NUM_REASONS: Record<number, string> = {
  1: '万物之始，今天适合做一件只有你自己知道的小事',
  2: '一分为二，今天的纠结会比平时多一倍，但都不重要',
  3: '三人成众，今天大概率要被拉进一个不想进的群',
  4: '据说不吉利，但其实你今天会发现"四舍五入"很好用',
  5: '中庸之道，今天点的外卖大概率是 5 星好评但味道一般',
  6: '六六大顺，今天会有 6 件小事卡你三秒，然后又顺利通过',
  7: '七窍玲珑，今天朋友圈第 7 条会让你停下来多看两眼',
  8: '发的谐音，但今天发的可能是脾气，不是财',
  9: '九九归一，今天会想起一件 9 天前没做完的事',
}

const YIDOS = [
  '把"在忙"作为今日统一回复模板',
  '午饭后散步十分钟，假装自己很健康',
  '给最近一次帮过你的人发条"谢谢"',
  '把工位上那杯凉了的水换成热的',
  '今天少看一次手机时间',
  '把"明天再说"的事真的推到明天',
  '在文档里写一行只有自己看得懂的注释',
  '今天理直气壮地拒绝一件不想做的事',
  '把屏幕亮度调低一档，护眼也护心情',
  '中午随便点一道没吃过的菜',
  '路过镜子时对自己笑一下',
  '今天回家路上听一首老歌',
  '把那条收藏了三个月的视频看了',
  '给桌面换个干净的壁纸',
  '今天早睡半小时，从晚睡开始',
]

const LUCKY_ACTIONS = [
  '今天穿两只不一样的袜子出门，气场两倍',
  '建议对着镜子喊三声"今天我最棒"，不保证有用但很好玩',
  '中午吃饭时换一个新座位，运势随之流动',
  '今天发一条无人回应的朋友圈，练习接受沉默',
  '用左手刷五分钟手机，开发右脑，据说',
  '喝水时许个无关紧要的小愿望，成功率 50%（不喝不算）',
  '今天回复消息前深吸一口气，防止冲动发言',
  '中午随机点一道从没吃过的菜，突破命运锁链',
  '走路时数自己的步数，数到 17 停一下，据说有效',
  '今天少看一次时间，感受时间的不存在',
  '给手机换一张壁纸，视觉刷新等于命运刷新',
  '今天主动说一句"辛苦了"，积累人品值',
]

// ── 生成今日运势 ──────────────────────────────────────────────────────
function generateFortune(extraSalt = 0) {
  const rng = seedRng(dateSeed() + extraSalt)
  const fortune = pick(rng, FORTUNES)
  const overall = pick(rng, OVERALL_LEVELS)
  const luckyNum = Math.floor(rng() * 9) + 1
  const luckyReason = LUCKY_NUM_REASONS[luckyNum]
  const yidos = pickN(rng, YIDOS, 2)
  const action = pick(rng, LUCKY_ACTIONS)
  return { fortune, overall, luckyNum, luckyReason, yidos, action }
}

// ── 状态 ─────────────────────────────────────────────────────────────
const rerollCount = ref(0)
const data = ref(generateFortune(0))
const shaking = ref(false)
const sharing = ref(false)
const cardRef = ref<HTMLElement | null>(null)
const cardBgUrl = '/tools/fortune-card-bg.png'

function reroll() {
  if (shaking.value) return
  shaking.value = true
  setTimeout(() => {
    rerollCount.value++
    data.value = generateFortune(rerollCount.value)
    shaking.value = false
  }, 600)
}

// ── 分享 ─────────────────────────────────────────────────────────────
async function shareCard() {
  if (!cardRef.value || sharing.value) return
  sharing.value = true
  try {
    const canvas = await html2canvas(cardRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: null,
    })
    const link = document.createElement('a')
    link.download = `今日运势_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (e) {
    console.error('生成图片失败', e)
  } finally {
    sharing.value = false
  }
}

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})
</script>

<template>
  <div class="fortune-widget">
    <!-- 签文区（点击摇一摇） -->
    <div class="sign-area" :class="{ shaking }" @click="reroll" title="点击重新占卜">
      <div class="sign-badge">今日签</div>
      <div class="sign-text">
        <span class="sign-yi">宜&nbsp;{{ data.fortune.yi }}</span>
        <span class="sign-sep">·</span>
        <span class="sign-ji">忌&nbsp;{{ data.fortune.ji }}</span>
      </div>
      <div class="sign-hint">点击签文可重新占卜</div>
    </div>

    <!-- 详细报告 -->
    <div class="report">
      <!-- 综合运势 -->
      <div class="report-section">
        <div class="section-header">
          <span class="section-icon">☯</span>
          <span class="section-title">综合运势</span>
          <span class="section-tag" :class="data.overall.score < 50 ? 'bad' : 'good'">
            {{ data.overall.label }}
          </span>
        </div>
        <div class="bar-wrap">
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: data.overall.score + '%' }" />
          </div>
          <span class="bar-score">{{ data.overall.score }}</span>
        </div>
        <p class="section-desc">{{ data.overall.desc }}</p>
      </div>

      <!-- 幸运数字 -->
      <div class="report-section">
        <div class="section-header">
          <span class="section-icon">✦</span>
          <span class="section-title">幸运数字</span>
        </div>
        <div class="lucky-num-row">
          <span class="lucky-num">{{ data.luckyNum }}</span>
          <span class="lucky-reason">{{ data.luckyReason }}</span>
        </div>
      </div>

      <!-- 今日宜做 -->
      <div class="report-section">
        <div class="section-header">
          <span class="section-icon">✿</span>
          <span class="section-title">今日宜做</span>
        </div>
        <div class="tag-list">
          <span v-for="t in data.yidos" :key="t" class="yido-tag">宜：{{ t }}</span>
        </div>
      </div>

      <!-- 幸运行动 -->
      <div class="report-section">
        <div class="section-header">
          <span class="section-icon">⚡</span>
          <span class="section-title">幸运行动</span>
        </div>
        <p class="section-desc action-desc">{{ data.action }}</p>
      </div>
    </div>

    <!-- 分享按钮 -->
    <button class="share-btn" :disabled="sharing" @click="shareCard">
      {{ sharing ? '生成中…' : '分享今日运势' }}
    </button>

    <!-- 隐藏卡片（用于截图，渲染在屏外） -->
    <div class="card-offscreen">
      <div ref="cardRef" class="share-card">
        <img :src="cardBgUrl" class="card-bg" alt="" />
        <div class="card-content">
          <p class="card-date">{{ today }} 今日运势</p>
          <div class="card-sign">
            <span>宜 {{ data.fortune.yi }}</span>
            <span class="card-sep">·</span>
            <span>忌 {{ data.fortune.ji }}</span>
          </div>
          <div class="card-rows">
            <div class="card-row"><span class="cr-label">综合运势</span><span class="cr-val">{{ data.overall.label }}（{{ data.overall.score }}分）</span></div>
            <div class="card-row"><span class="cr-label">幸运数字</span><span class="cr-val">{{ data.luckyNum }}</span></div>
            <div class="card-row"><span class="cr-label">今日宜做</span><span class="cr-val">{{ data.yidos.join(' / ') }}</span></div>
            <div class="card-row"><span class="cr-label">幸运行动</span><span class="cr-val">{{ data.action }}</span></div>
          </div>
          <p class="card-footer">起风了 · 赛博算命摊</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fortune-widget {
  width: 100%;
  padding-bottom: 1.25rem;
}

/* 签文 */
.sign-area {
  text-align: center;
  padding: 1.5rem 1rem 1.25rem;
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid var(--qi-border);
  transition: background .2s;
}
.sign-area:hover { background: rgba(255,140,90,.04); }
.sign-badge {
  display: inline-block;
  font-size: .68rem; font-weight: 700;
  padding: 2px 8px; border-radius: 999px;
  background: rgba(255,140,90,.12);
  color: var(--qi-primary);
  margin-bottom: .6rem;
  letter-spacing: .08em;
}
.sign-text {
  display: flex; align-items: center; justify-content: center;
  gap: .75rem;
  font-family: 'Noto Serif SC', serif;
  font-size: 1.25rem; font-weight: 700;
  margin-bottom: .4rem;
}
.sign-yi { color: var(--qi-primary); }
.sign-sep { color: var(--qi-ink-light); }
.sign-ji { color: var(--qi-ink-muted); }
.sign-hint { font-size: .68rem; color: var(--qi-ink-light); }

/* 摇一摇动画 */
@keyframes shake {
  0%   { transform: rotate(0deg); }
  15%  { transform: rotate(-4deg); }
  30%  { transform: rotate(4deg); }
  45%  { transform: rotate(-3deg); }
  60%  { transform: rotate(3deg); }
  75%  { transform: rotate(-1deg); }
  100% { transform: rotate(0deg); }
}
.sign-area.shaking { animation: shake .6s ease; }

/* 报告 */
.report { padding: .875rem 1rem 0; display: flex; flex-direction: column; gap: .875rem; }

.report-section { display: flex; flex-direction: column; gap: .45rem; }
.section-header { display: flex; align-items: center; gap: .4rem; }
.section-icon { font-size: .85rem; color: var(--qi-primary); opacity: .75; width: 16px; text-align: center; }
.section-title { font-size: .82rem; font-weight: 600; color: var(--qi-ink); }
.section-tag {
  font-size: .68rem; font-weight: 700; padding: 1px 7px;
  border-radius: 999px; margin-left: auto;
}
.section-tag.bad  { background: rgba(240,80,80,.1);  color: #d94f4f; }
.section-tag.good { background: rgba(100,200,120,.12); color: #3a9c5a; }

/* 进度条 */
.bar-wrap { display: flex; align-items: center; gap: .6rem; padding-left: 1.4rem; }
.bar-track { flex: 1; height: 6px; border-radius: 999px; background: var(--qi-bg-muted); overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; background: var(--qi-primary); transition: width .6s ease; }
.bar-score { font-size: .75rem; font-weight: 700; color: var(--qi-ink-muted); min-width: 24px; text-align: right; }

.section-desc {
  font-size: .82rem; color: var(--qi-ink-muted);
  line-height: 1.6; padding-left: 1.4rem;
}
.action-desc { color: var(--qi-ink); }

/* 幸运数字 */
.lucky-num-row { display: flex; align-items: baseline; gap: .75rem; padding-left: 1.4rem; }
.lucky-num { font-size: 2rem; font-weight: 800; color: var(--qi-primary); line-height: 1; font-variant-numeric: tabular-nums; }
.lucky-reason { font-size: .8rem; color: var(--qi-ink-muted); line-height: 1.5; }

/* 宜做标签 */
.tag-list { display: flex; flex-wrap: wrap; gap: .4rem; padding-left: 1.4rem; }
.yido-tag {
  font-size: .75rem; padding: 3px 9px; border-radius: 6px;
  background: rgba(168, 216, 192, 0.15); color: #3a8a6a;
  border: 1px solid rgba(120, 180, 150, 0.25);
}

/* 分享按钮 */
.share-btn {
  display: block; margin: 1.25rem 1rem 0;
  width: calc(100% - 2rem);
  padding: .55rem;
  border-radius: 10px; border: 1.5px solid var(--qi-border);
  background: none; color: var(--qi-ink-muted);
  font-size: .84rem; font-weight: 500; cursor: pointer;
  transition: all .2s;
}
.share-btn:hover:not(:disabled) {
  border-color: var(--qi-primary); color: var(--qi-primary);
  background: rgba(255,140,90,.05);
}
.share-btn:disabled { opacity: .5; cursor: default; }

/* 截图卡片（屏外渲染） */
.card-offscreen {
  position: fixed; left: -9999px; top: 0;
  pointer-events: none; opacity: 0;
}
.share-card {
  position: relative;
  width: 600px; height: 800px;
  border-radius: 20px; overflow: hidden;
  font-family: 'Noto Serif SC', 'PingFang SC', sans-serif;
}
.card-bg {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
}
.card-content {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: flex-end;
  padding: 2.5rem 2.5rem 3rem;
  gap: 1rem;
}
.card-date { font-size: .9rem; color: #8a7060; font-weight: 500; }
.card-sign {
  display: flex; align-items: center; gap: 1rem;
  font-size: 1.5rem; font-weight: 800; color: #3a2a1a;
}
.card-sep { color: #c4a898; }
.card-rows { width: 100%; display: flex; flex-direction: column; gap: .5rem; }
.card-row {
  display: flex; gap: .75rem; align-items: flex-start;
  background: rgba(255,248,240,.7); border-radius: 8px; padding: .45rem .75rem;
}
.cr-label { font-size: .8rem; color: #ff8c5a; font-weight: 700; flex-shrink: 0; min-width: 52px; }
.cr-val { font-size: .8rem; color: #3a2a1a; line-height: 1.5; }
.card-footer { font-size: .72rem; color: #8a7060; margin-top: .25rem; }
</style>
