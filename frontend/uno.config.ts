import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss'
import transformerDirectives from '@unocss/transformer-directives'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
    }),
  ],
  transformers: [
    transformerDirectives(),
  ],
  theme: {
    fontFamily: {
      serif: ['Noto Serif SC', 'Songti SC', 'serif'],
      sans: ['Inter', 'PingFang SC', '苹方', 'sans-serif'],
      mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
    },
  },
  shortcuts: {
    'qi-card': 'bg-[var(--qi-bg-card)] rounded-2xl p-6 shadow-[0_4px_16px_var(--qi-shadow)]',
    'qi-btn': 'rounded-full px-6 py-2 font-sans font-500 transition-all duration-200',
    'qi-btn-primary': 'qi-btn bg-[var(--qi-primary)] text-white hover:opacity-90 hover:-translate-y-0.5',
    'qi-tag': 'rounded-full px-3 py-1 text-12px font-500',
  }
})
