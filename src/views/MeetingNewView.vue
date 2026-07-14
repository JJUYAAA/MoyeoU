<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createMeeting } from '@/services/api'

const route = useRoute()
const router = useRouter()

const categories = ['모각코·스터디', 'CS·알고리즘', '점심·저녁', '프로젝트·팀원', '운동·산책', '취준·정보공유']

const form = ref({
  title: '',
  category: categories[0],
  date: '',
  time: '',
  location: '',
  max: 4,
  description: '',
  password: '',
})

const submitted = ref(false)

onMounted(() => {
  // 장소 페이지에서 넘어온 경우 장소를 미리 채웁니다.
  if (route.query.place) {
    form.value.location = String(route.query.place)
  }
})

async function submit() {
  await createMeeting({ ...form.value })
  submitted.value = true
  // 잠시 성공 메시지를 보여준 뒤 목록으로 이동합니다.
  setTimeout(() => router.push('/meetings'), 1200)
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-6 py-10">
    <h1 class="mb-6 text-3xl font-bold text-ink">모임 만들기</h1>

    <p v-if="submitted" class="mb-6 rounded-lg bg-brand-light px-4 py-3 text-brand-hover">
      모임이 등록되었어요! 목록으로 이동합니다...
    </p>

    <form class="space-y-5 rounded-xl border border-line bg-white p-6" @submit.prevent="submit">
      <div>
        <label class="field-label">제목</label>
        <input v-model="form.title" type="text" required class="field-input" placeholder="예: 오늘 저녁 알고리즘 모각코" />
      </div>

      <div>
        <label class="field-label">카테고리</label>
        <select v-model="form.category" class="field-input">
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="field-label">날짜</label>
          <input v-model="form.date" type="text" required class="field-input" placeholder="예: 오늘, 토요일" />
        </div>
        <div>
          <label class="field-label">시간</label>
          <input v-model="form.time" type="time" required class="field-input" />
        </div>
      </div>

      <div>
        <label class="field-label">장소</label>
        <input v-model="form.location" type="text" required class="field-input" placeholder="예: SSAFY 대전 캠퍼스 스터디룸 A" />
      </div>

      <div>
        <label class="field-label">최대 모집 인원</label>
        <input v-model.number="form.max" type="number" min="2" max="20" required class="field-input" />
      </div>

      <div>
        <label class="field-label">상세 내용</label>
        <textarea v-model="form.description" rows="4" class="field-input" placeholder="모임에 대해 자유롭게 소개해주세요."></textarea>
      </div>

      <div>
        <label class="field-label">수정·삭제용 비밀번호</label>
        <input v-model="form.password" type="password" required class="field-input" placeholder="모임 관리를 위한 비밀번호" />
      </div>

      <button type="submit" class="btn-primary w-full">모임 등록하기</button>
    </form>
  </div>
</template>
