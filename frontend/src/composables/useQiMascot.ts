import { computed } from 'vue'
import { useScrollProgress } from './useScrollProgress'
import type { MascotState } from '@/types'

export function useQiMascot() {
  const { progress } = useScrollProgress()

  const currentState = computed<MascotState>(() => {
    if (progress.value < 0.25) return 'wave'
    if (progress.value < 0.45) return 'think'
    if (progress.value < 0.65) return 'type'
    if (progress.value < 0.85) return 'singing'
    return 'wind'
  })

  return { currentState }
}
