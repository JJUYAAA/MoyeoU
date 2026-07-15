<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getMeetings, getLocations } from "@/services/api";
import AiSearchBar from "@/components/AiSearchBar.vue";
import MeetingCard from "@/components/MeetingCard.vue";
import PlaceCard from "@/components/PlaceCard.vue";
import serviceLogo from "@/assets/moyeou_logo.svg";

const router = useRouter();
const meetings = ref([]);
const places = ref([]);

const suggestions = [
  "오늘 알고리즘 모각코 있어?",
  "점심 같이 먹을 사람",
  "관통 프로젝트 팀원 구해요",
];

onMounted(async () => {
  // 모임 목록(Meetings) 안전하게 가져와서 3개만 자르기
  const meetingsData = await getMeetings();
  // 백엔드 규격 { items: [...] } 구조인지 검사하여 안전하게 배열만 추출
  const meetingsList =
    meetingsData && meetingsData.items
      ? meetingsData.items
      : Array.isArray(meetingsData)
        ? meetingsData
        : [];

  meetings.value = meetingsList.slice(0, 3);

  // 장소 목록(Locations) 안전하게 가져와서 3개만 자르기
  const locationsData = await getLocations();
  const locationsList = Array.isArray(locationsData) ? locationsData : [];

  places.value = locationsList.slice(0, 3);
});

function handleSearch(query) {
  // 검색어를 모임 찾기 페이지로 전달합니다.
  router.push({ path: "/meetings", query: { q: query } });
}
</script>

<template>
  <section class="bg-white">
    <div class="mx-auto max-w-6xl px-6 py-12 text-center flex flex-col items-center">
      <div class="mb-1 transition-transform duration-300 hover:scale-105 active:scale-95">
        <img
          :src="serviceLogo"
          alt="SSAFY 모여유 로고"
          class="mx-auto h-40 w-auto object-contain drop-shadow-md"
        />
      </div>

      <h1 class="mt-0 text-balance text-4xl font-bold text-ink md:text-5xl">
        교육 끝나고, 누구와 함께할까요?
      </h1>
      <p class="mx-auto mt-4 max-w-2xl text-pretty text-lg leading-relaxed text-ink/70">
        모각코·CS 스터디부터 프로젝트 팀원, 점심 메이트, 러닝까지. 같은 기수 동료들과 번개로 모여요.
      </p>
      <div class="mx-auto mt-8 max-w-2xl w-full">
        <AiSearchBar :suggestions="suggestions" @search="handleSearch" />
      </div>
    </div>
  </section>

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

  <section class="mx-auto max-w-6xl px-6 pb-16">
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-2xl font-bold text-ink">캠퍼스 주변, 같이 가볼까요?</h2>
      <RouterLink to="/locations" class="text-sm font-medium text-brand hover:text-brand-hover">
        전체 보기
      </RouterLink>
    </div>
    <div class="grid gap-5 md:grid-cols-3">
      <PlaceCard v-for="p in places" :key="p.id" :place="p" />
    </div>
  </section>
</template>
