<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getMeetings } from '@/services/api'
import MeetingCard from '@/components/MeetingCard.vue'
import CategoryFilter from '@/components/CategoryFilter.vue'

const route = useRoute()

const meetings = ref([])
const keyword = ref(route.query.q ? String(route.query.q) : '')
const selectedCategory = ref('전체')
const onlyOpen = ref(false)

const categories = ['전체', '모각코·스터디', 'CS·알고리즘', '점심·저녁', '프로젝트·팀원', '운동·산책', '취준·정보공유']

onMounted(async () => {
  meetings.value = await getMeetings()
})

const filteredMeetings = computed(() => {
  // 문장으로 검색해도 매칭되도록 공백 단위로 나눠서 확인합니다.
  const tokens = keyword.value.trim().split(/\s+/).filter(Boolean)
  return meetings.value.filter((m) => {
    const haystack = `${m.title} ${m.location} ${m.category} ${m.description}`
    const matchKeyword =
      tokens.length === 0 || tokens.some((t) => haystack.includes(t))
    const matchCategory =
      selectedCategory.value === '전체' || m.category === selectedCategory.value
    const matchOpen = !onlyOpen.value || m.status === 'OPEN'
    return matchKeyword && matchCategory && matchOpen
  })
})
</script>

<template>
  <div class="mx-auto max-w-6xl px-6 py-10">
    <h1 class="mb-6 text-3xl font-bold text-ink">모임 찾기</h1>

    <div class="mb-6 space-y-4 rounded-xl border border-line bg-white p-5">
      <input
        v-model="keyword"
        type="text"
        placeholder="키워드로 검색 (예: 모각코, 알고리즘, 프로젝트)"
        class="field-input"
      />
      <CategoryFilter :categories="categories" v-model="selectedCategory" />
      <label class="flex w-fit cursor-pointer items-center gap-2 text-sm text-ink/80">
        <input v-model="onlyOpen" type="checkbox" class="h-4 w-4 accent-brand" />
        모집 중만 보기
      </label>
    </div>

    <div v-if="filteredMeetings.length" class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <MeetingCard v-for="m in filteredMeetings" :key="m.id" :meeting="m" />
    </div>
    <p v-else class="py-16 text-center text-ink/50">조건에 맞는 모임이 없어요.</p>
  </div>
</template>
