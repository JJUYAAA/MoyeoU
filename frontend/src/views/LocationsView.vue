<script setup>
import { ref, computed, onMounted } from 'vue'
import { getLocations } from '@/services/api'
import PlaceCard from '@/components/PlaceCard.vue'
import CategoryFilter from '@/components/CategoryFilter.vue'

const places = ref([])
const selectedCategory = ref('전체')

const categories = ['전체', '캠퍼스', '스터디', '맛집', '운동·산책', '카페', '휴식']

onMounted(async () => {
  places.value = await getLocations()
})

const filteredPlaces = computed(() => {
  if (selectedCategory.value === '전체') return places.value
  return places.value.filter((p) => p.type === selectedCategory.value)
})
</script>

<template>
  <div class="mx-auto max-w-6xl px-6 py-10">
    <h1 class="mb-2 text-3xl font-bold text-ink">캠퍼스 주변</h1>
    <p class="mb-6 text-ink/70">
      SSAFY 대전 캠퍼스 근처 스터디·맛집·운동 스팟을 둘러보고 함께 갈 동료를 모집해보세요.
    </p>

    <div class="mb-6">
      <CategoryFilter :categories="categories" v-model="selectedCategory" />
    </div>

    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <PlaceCard v-for="p in filteredPlaces" :key="p.id" :place="p" />
    </div>
  </div>
</template>
