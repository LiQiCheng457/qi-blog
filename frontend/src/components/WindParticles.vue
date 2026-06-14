<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref<HTMLCanvasElement | null>(null)
let animId: number
let mouseX = 0
let mouseY = 0

interface Leaf {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  color: string
  rotation: number
  rotSpeed: number
}

const COLORS = ['#A8D8C0', '#FFD166', '#F4A0A0']

function createLeaf(w: number, h: number): Leaf {
  return {
    x: Math.random() * w,
    y: Math.random() * h,
    vx: (Math.random() - 0.5) * 0.4,
    vy: Math.random() * 0.3 + 0.1,
    size: Math.random() * 4 + 4,
    opacity: Math.random() * 0.3 + 0.3,
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
    rotation: Math.random() * Math.PI * 2,
    rotSpeed: (Math.random() - 0.5) * 0.02,
  }
}

onMounted(() => {
  const c = canvas.value!
  const ctx = c.getContext('2d')!

  const resize = () => {
    c.width = window.innerWidth
    c.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)

  const leaves: Leaf[] = Array.from({ length: 7 }, () => createLeaf(c.width, c.height))

  const onMouse = (e: MouseEvent) => {
    mouseX = e.clientX
    mouseY = e.clientY
  }
  window.addEventListener('mousemove', onMouse, { passive: true })

  const draw = () => {
    ctx.clearRect(0, 0, c.width, c.height)

    for (const leaf of leaves) {
      // 视差偏移
      const dx = (mouseX - c.width / 2) * 0.02
      const dy = (mouseY - c.height / 2) * 0.02

      leaf.x += leaf.vx + dx * 0.01
      leaf.y += leaf.vy
      leaf.rotation += leaf.rotSpeed

      // 超出边界重置
      if (leaf.y > c.height + 20) {
        leaf.y = -20
        leaf.x = Math.random() * c.width
      }
      if (leaf.x < -20) leaf.x = c.width + 20
      if (leaf.x > c.width + 20) leaf.x = -20

      ctx.save()
      ctx.translate(leaf.x + dx, leaf.y + dy)
      ctx.rotate(leaf.rotation)
      ctx.globalAlpha = leaf.opacity
      ctx.fillStyle = leaf.color
      // 像素风格小方块
      ctx.fillRect(-leaf.size / 2, -leaf.size / 2, leaf.size, leaf.size)
      ctx.restore()
    }

    animId = requestAnimationFrame(draw)
  }

  draw()

  onUnmounted(() => {
    cancelAnimationFrame(animId)
    window.removeEventListener('resize', resize)
    window.removeEventListener('mousemove', onMouse)
  })
})
</script>

<template>
  <canvas
    ref="canvas"
    style="position:fixed;inset:0;pointer-events:none;z-index:0;"
    aria-hidden="true"
  />
</template>
