<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getMeetingById } from '@/services/api'
import BaseModal from '@/components/BaseModal.vue'

const route = useRoute()

const meeting = ref(null)
const loading = ref(true)

const showJoinModal = ref(false)
const joined = ref(false)
const form = ref({ nickname: '', password: '' })

onMounted(async () => {
  meeting.value = await getMeetingById(route.params.id)
  loading.value = false
})

function join() {
  if (!form.value.nickname || !form.value.password) return
  joined.value = true
}

function closeModal() {
  showJoinModal.value = false
  joined.value = false
  form.value = { nickname: '', password: '' }
}
</script>

<template>
  <div class="mx-auto max-w-3xl px-6 py-10">
    <RouterLink to="/meetings" class="text-sm text-brand hover:text-brand-hover">
      &larr; 모임 목록으로
    </RouterLink>

    <p v-if="loading" class="py-16 text-center text-ink/50">불러오는 중...</p>
    <p v-else-if="!meeting" class="py-16 text-center text-ink/50">모임을 찾을 수 없어요.</p>

    <div v-else class="mt-4 rounded-xl border border-line bg-white p-6">
      <div class="mb-4 flex items-center gap-2">
        <span class="rounded-full bg-brand-light px-2.5 py-1 text-xs font-medium text-brand-hover">
          {{ meeting.category }}
        </span>
        <span
          class="rounded-full px-2.5 py-1 text-xs font-medium"
          :class="meeting.status === 'OPEN' ? 'bg-brand text-white' : 'bg-line text-ink/60'"
        >
          {{ meeting.status === 'OPEN' ? '모집 중' : '마감' }}
        </span>
      </div>

      <h1 class="mb-4 text-2xl font-bold text-ink">{{ meeting.title }}</h1>

      <dl class="mb-6 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt class="text-ink/50">일시</dt>
          <dd class="font-medium text-ink">{{ meeting.date }} {{ meeting.time }}</dd>
        </div>
        <div>
          <dt class="text-ink/50">장소</dt>
          <dd class="font-medium text-ink">{{ meeting.location }}</dd>
        </div>
        <div>
          <dt class="text-ink/50">참여 인원</dt>
          <dd class="font-medium text-ink">{{ meeting.current }} / {{ meeting.max }}명</dd>
        </div>
      </dl>

      <div class="mb-6">
        <h2 class="mb-2 font-semibold text-ink">상세 내용</h2>
        <p class="leading-relaxed text-ink/80">{{ meeting.description }}</p>
      </div>

      <p class="mb-6 rounded-lg bg-brand-light px-4 py-3 text-sm text-brand-hover">
        개인정보 공유를 피하고, 공개된 장소에서 만나는 것을 권장합니다.
      </p>

      <div class="flex gap-2">
        <button type="button" class="btn-primary flex-1" @click="showJoinModal = true">
          참여하기
        </button>
        <button type="button" class="btn-outline" @click="alert('수정 기능은 준비 중입니다.')">
          수정
        </button>
      </div>
    </div>

    <!-- 참여 모달 -->
    <BaseModal :open="showJoinModal" title="모임 참여하기" @close="closeModal">
      <div v-if="!joined" class="space-y-4">
        <div>
          <label class="field-label">닉네임</label>
          <input v-model="form.nickname" type="text" class="field-input" placeholder="사용할 닉네임" />
        </div>
        <div>
          <label class="field-label">참여 비밀번호</label>
          <input v-model="form.password" type="password" class="field-input" placeholder="참여 확인용 비밀번호" />
        </div>
        <button type="button" class="btn-primary w-full" @click="join">참여 신청</button>
      </div>
      <div v-else class="py-4 text-center">
        <p class="mb-4 text-ink">참여 신청이 완료되었어요! 공개된 장소에서 안전하게 만나세요.</p>
        <button type="button" class="btn-outline" @click="closeModal">닫기</button>
      </div>
    </BaseModal>
  </div>
</template>
