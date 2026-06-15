<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import QiMascot from '@/components/QiMascot.vue'
import BackToTop from '@/components/BackToTop.vue'
import ChatWidget from '@/components/ChatWidget.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { useUserStore } from '@/stores/user'
import { isPageLoading } from '@/router'

const userStore = useUserStore()
const route   = useRoute()
const isAdmin = computed(() => route.path.startsWith('/admin'))

const showChat   = ref(false)
const showBubble = ref(false)

onMounted(() => {
  userStore.init()
  setTimeout(() => { showBubble.value = true }, 2000)
  setTimeout(() => { showBubble.value = false }, 7000)
})

function toggleChat() {
  showChat.value = !showChat.value
  showBubble.value = false
}
</script>

<template>
  <NavBar v-if="!isAdmin" />
  <main>
    <RouterView v-slot="{ Component }">
      <Transition name="page">
        <div :key="route.path" class="page-slot">
          <component :is="Component" />
        </div>
      </Transition>
    </RouterView>
  </main>

  <LoadingOverlay :show="isPageLoading" />

  <template v-if="!isAdmin">
    <!-- 水豚聊天触发器 -->
    <div class="qi-fixed-mascot" @click="toggleChat">
      <!-- 气泡邀请 -->
      <Transition name="bubble">
        <div v-if="showBubble && !showChat" class="chat-bubble">
          可以来和我聊天哦~
        </div>
      </Transition>
      <QiMascot :auto-switch="true" size="small" />
    </div>

    <!-- 聊天面板 -->
    <ChatWidget :open="showChat" @close="showChat = false" />

    <BackToTop />
  </template>
</template>

<style>
.page-slot { position: relative; }
.page-enter-active { transition: opacity 0.22s ease, transform 0.22s ease; }
.page-leave-active {
  transition: opacity 0.18s ease;
  position: absolute; top: 0; left: 0; right: 0;
  pointer-events: none;
}
.page-enter-from { opacity: 0; transform: translateY(8px); }
.page-leave-to { opacity: 0; }
</style>

<style scoped>
.qi-fixed-mascot {
  position: fixed;
  right: 2rem;
  bottom: 2rem;
  z-index: 150;
  cursor: pointer;
  /* 移除 pointer-events: none，让它可点击 */
}

/* 悬停时水豚轻微上浮 */
.qi-fixed-mascot:hover { transform: translateY(-4px); transition: transform .25s ease; }
.qi-fixed-mascot:not(:hover) { transition: transform .25s ease; }

/* 气泡 */
.chat-bubble {
  position: absolute;
  bottom: calc(100% + 10px);
  right: 0;
  background: var(--qi-bg-card);
  border: 1.5px solid var(--qi-border);
  border-radius: 14px 14px 4px 14px;
  padding: .5rem .85rem;
  font-size: 13px;
  color: var(--qi-ink);
  white-space: nowrap;
  box-shadow: 0 4px 18px rgba(0, 0, 0, .1);
  pointer-events: none;
}

.chat-bubble::after {
  content: '';
  position: absolute;
  bottom: -6px;
  right: 14px;
  width: 10px;
  height: 10px;
  background: var(--qi-bg-card);
  border-right: 1.5px solid var(--qi-border);
  border-bottom: 1.5px solid var(--qi-border);
  transform: rotate(45deg);
}

.bubble-enter-active { transition: opacity .3s ease, transform .3s ease; }
.bubble-leave-active { transition: opacity .2s ease, transform .2s ease; }
.bubble-enter-from { opacity: 0; transform: translateY(6px); }
.bubble-leave-to { opacity: 0; transform: translateY(4px); }

@media (max-width: 768px) {
  .qi-fixed-mascot {
    right: 1rem;
    bottom: 1rem;
    transform: scale(0.75);
    transform-origin: bottom right;
  }
  .qi-fixed-mascot:hover { transform: scale(0.75) translateY(-4px); }
}
</style>
