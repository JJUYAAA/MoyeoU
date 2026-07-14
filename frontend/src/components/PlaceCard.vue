<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  place: {
    type: Object,
    required: true,
  },
})

const router = useRouter()

function createMeetingHere() {
  router.push({ path: '/meetings/new', query: { place: props.place.name } })
}

function showDetail() {
  // 목업: 상세 정보는 알림으로 간단히 안내합니다.
  alert(`${props.place.name}\n종류: ${props.place.type}\n주소: ${props.place.address}`)
}
</script>

<template>
  <div class="card flex flex-col">
    <span class="mb-2 w-fit rounded-full bg-brand-light px-2.5 py-1 text-xs font-medium text-brand-hover">
      {{ place.type }}
    </span>
    <h3 class="mb-1 text-lg font-semibold text-ink">{{ place.name }}</h3>
    <p class="mb-4 flex-1 text-sm text-ink/70">{{ place.address }}</p>

    <div class="flex gap-2">
      <button type="button" class="btn-outline flex-1 text-sm" @click="showDetail">
        상세 보기
      </button>
      <button type="button" class="btn-primary flex-1 text-sm" @click="createMeetingHere">
        여기서 모임 만들기
      </button>
    </div>
  </div>
</template>
