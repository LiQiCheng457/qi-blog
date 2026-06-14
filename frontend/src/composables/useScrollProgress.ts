import { ref, onMounted, onUnmounted } from 'vue'

export function useScrollProgress() {
  const progress = ref(0)

  const onScroll = () => {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement
    const total = scrollHeight - clientHeight
    progress.value = total > 0 ? scrollTop / total : 0
  }

  onMounted(() => {
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
  })

  onUnmounted(() => {
    window.removeEventListener('scroll', onScroll)
  })

  return { progress }
}
