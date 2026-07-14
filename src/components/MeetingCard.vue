<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  meeting: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <RouterLink :to="`/meetings/${meeting.id}`" class="card block">
    <div class="mb-3 flex items-center justify-between gap-2">
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

    <h3 class="mb-2 text-lg font-semibold text-ink">{{ meeting.title }}</h3>

    <ul class="space-y-1 text-sm text-ink/70">
      <li>일시 · {{ meeting.date }} {{ meeting.time }}</li>
      <li>장소 · {{ meeting.location }}</li>
      <li>인원 · {{ meeting.current }} / {{ meeting.max }}명</li>
    </ul>
  </RouterLink>
</template>
