<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMeetings, getLocations } from '@/services/api'
import AiSearchBar from '@/components/AiSearchBar.vue'
import MeetingCard from '@/components/MeetingCard.vue'
import PlaceCard from '@/components/PlaceCard.vue'

const router = useRouter()
const meetings = ref([])
const places = ref([])

const suggestions = ['오늘 모각코 있어?', '같이 저녁 먹을 사람', '이번 주말 러닝']

onMounted(async () => {
  meetings.value = (await getMeetings()).slice(0, 3)
  places.value = (await getLocations()).slice(0, 3)
})

function handleSearch(query) {
  // 검색어를 모임 찾기 페이지로 전달합니다.
  router.push({ path: '/meetings', query: { q: query } })
}
</script>

<template>
  <!-- 히어로 -->
  <section class="bg-white">
    <div class="mx-auto max-w-6xl px-6 py-16 text-center">
      <h1 class="text-balance text-4xl font-bold text-ink md:text-5xl">
        오늘, 누구와 함께할까요?
      </h1>
      <p class="mx-auto mt-4 max-w-2xl text-pretty text-lg leading-relaxed text-ink/70">
        모각코부터 러닝, 맛집, 축제까지 대전에서 함께할 사람을 찾아보세요.
      </p>
      <div class="mx-auto mt-8 max-w-2xl">
        <AiSearchBar :suggestions="suggestions" @search="handleSearch" />
      </div>
    </div>
  </section>

  <!-- 모집 중인 번개 -->
  <section class="mx-auto max-w-6xl px-6 py-12">
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-2xl font-bold text-ink">지금 모집 중인 번개</h2>
      <RouterLink to="/meetings" class="text-sm font-medium text-brand hover:text-brand-hover">
        전체 보기
      </RouterLink>
    </div>
    <div class="grid gap-5 md:grid-cols-3">
      <MeetingCard v-for="m in meetings" :key="m.id" :meeting="m" />
    </div>
  </section>

  <!-- 대전 장소 -->
  <section class="mx-auto max-w-6xl px-6 pb-16">
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-2xl font-bold text-ink">대전에서 같이 가볼까요?</h2>
      <RouterLink to="/locations" class="text-sm font-medium text-brand hover:text-brand-hover">
        전체 보기
      </RouterLink>
    </div>
    <div class="grid gap-5 md:grid-cols-3">
      <PlaceCard v-for="p in places" :key="p.id" :place="p" />
    </div>
  </section>
</template>
