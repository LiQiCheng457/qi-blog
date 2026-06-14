import { ref, onMounted, onUnmounted } from 'vue'

export function useTyping(text: string, options?: { delay?: number; speed?: number }) {
  const { delay = 0, speed = 60 } = options ?? {}
  const displayed = ref('')
  const done = ref(false)

  let timeoutId: ReturnType<typeof setTimeout>
  let intervalId: ReturnType<typeof setInterval>

  onMounted(() => {
    timeoutId = setTimeout(() => {
      let i = 0
      intervalId = setInterval(() => {
        if (i < text.length) {
          displayed.value += text[i]
          i++
        } else {
          clearInterval(intervalId)
          done.value = true
        }
      }, speed)
    }, delay)
  })

  onUnmounted(() => {
    clearTimeout(timeoutId)
    clearInterval(intervalId)
  })

  return { displayed, done }
}
