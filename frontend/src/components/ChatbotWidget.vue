<script setup>
import { ref, nextTick } from 'vue'
import { searchChat } from '@/services/api'
import MeetingCard from '@/components/MeetingCard.vue'

const open = ref(false)
const input = ref('')
const messages = ref([
  { role: 'bot', text: '안녕하세요! SSAFY 동료들과 함께할 모임을 자연스럽게 물어보세요.', results: [] },
])
const listRef = ref(null)

const suggestions = ['오늘 알고리즘 모각코 있어?', 'CS 면접 스터디 찾아줘', '점심 같이 먹을 사람 있어?']

async function send(text) {
  const query = (text ?? input.value).trim()
  if (!query) return

  messages.value.push({ role: 'user', text: query, results: [] })
  input.value = ''
  await scrollToBottom()

  const { reply, results } = await searchChat(query)
  messages.value.push({ role: 'bot', text: reply, results })
  await scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
}

function onKeydown(e) {
  if (e.isComposing || e.keyCode === 229) return
  send()
}
</script>

<template>
  <!-- 플로팅 버튼 -->
  <button
    type="button"
    class="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-brand text-white shadow-lg transition-colors hover:bg-brand-hover"
    aria-label="챗봇 열기"
    @click="open = !open"
  >
    <span class="text-sm font-semibold">{{ open ? '닫기' : 'AI' }}</span>
  </button>

  <!-- 챗 패널 -->
  <Transition name="slide">
    <div
      v-if="open"
      class="fixed bottom-24 right-6 z-50 flex h-[28rem] w-80 flex-col overflow-hidden rounded-xl border border-line bg-white shadow-xl"
    >
      <div class="border-b border-line bg-brand px-4 py-3 text-white">
        <p class="font-semibold">모여유 AI 도우미</p>
      </div>

      <div ref="listRef" class="flex-1 space-y-3 overflow-y-auto p-3">
        <div v-for="(msg, i) in messages" :key="i">
          <div
            class="max-w-[85%] rounded-lg px-3 py-2 text-sm"
            :class="msg.role === 'user'
              ? 'ml-auto bg-brand text-white'
              : 'bg-brand-light text-ink'"
          >
            {{ msg.text }}
          </div>
          <div v-if="msg.results && msg.results.length" class="mt-2 space-y-2">
            <MeetingCard v-for="m in msg.results" :key="m.id" :meeting="m" />
          </div>
        </div>
      </div>

      <div class="border-t border-line p-3">
        <div class="mb-2 flex flex-wrap gap-1.5">
          <button
            v-for="s in suggestions"
            :key="s"
            type="button"
            class="rounded-full border border-line px-2 py-1 text-xs text-ink/70 transition-colors hover:border-brand hover:text-brand"
            @click="send(s)"
          >
            {{ s }}
          </button>
        </div>
        <div class="flex gap-2">
          <input
            v-model="input"
            type="text"
            placeholder="메시지를 입력하세요"
            class="field-input flex-1 text-sm"
            @keydown.enter="onKeydown"
          />
          <button type="button" class="btn-primary text-sm" @click="send()">전송</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
