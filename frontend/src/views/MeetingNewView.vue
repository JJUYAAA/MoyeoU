<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createMeeting } from "@/services/api";

const route = useRoute();
const router = useRouter();

const categories = [
  "모각코·스터디",
  "CS·알고리즘",
  "점심·저녁",
  "프로젝트·팀원",
  "운동·산책",
  "취준·정보공유",
];

const form = ref({
  title: "",
  category: categories[0],
  date: "",
  time: "",
  location: "",
  max: 4,
  description: "",
  password: "",
  location_id: null, // 💡 백엔드 DB 연동을 위해 공공데이터 고유 ID를 담아둘 공간 추가!
});

const submitted = ref(false);

onMounted(() => {
  // ⚡ [공공데이터 연동 핵심]
  // PlaceCard.vue에서 보낸 'loc_name'과 'loc_id'를 정확하게 캐치해서 매핑합니다!
  if (route.query.loc_name) {
    form.value.location = String(route.query.loc_name);
  }
  if (route.query.loc_id) {
    form.value.location_id = String(route.query.loc_id);
  }
});

async function submit() {
  // 간단한 유효성 검사 (form 태그를 div로 바꿨기 때문에 직접 검증을 한 번 수행해 줍니다)
  if (
    !form.value.title ||
    !form.value.date ||
    !form.value.time ||
    !form.value.location ||
    !form.value.password
  ) {
    alert("필수 입력 항목(*)을 모두 입력해 주세요!");
    return;
  }

  try {
    // 1. 날짜 데이터 포맷 안정화 (백엔드는 YYYY-MM-DD 포맷을 기대합니다)
    let formattedDate = form.value.date;
    if (formattedDate === "오늘") {
      formattedDate = new Date().toISOString().split("T")[0];
    } else if (formattedDate === "내일") {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      formattedDate = tomorrow.toISOString().split("T")[0];
    } else {
      // 직접 입력했을 경우, 기입 형식이 안 맞으면 에러 방지를 위해 기본값 처리 혹은 파싱
      const dateReg = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateReg.test(formattedDate)) {
        // YYYY-MM-DD 형식이 아니면 일단 오늘 날짜로 보정하여 전송 실패 차단
        formattedDate = new Date().toISOString().split("T")[0];
      }
    }

    // 2. 시간 데이터 포맷 안정화 (HH:MM:SS 형식 확보)
    let formattedTime = form.value.time; // 예: "15:30"
    if (formattedTime && formattedTime.split(":").length === 2) {
      formattedTime = `${formattedTime}:00`; // 초(second) 정보가 없으면 ":00" 붙여서 "15:30:00" 포맷 완성
    }

    // 3. 백엔드 최종 규격 100% 일치 매핑 객체 (Payload)
    const backendPayload = {
      title: form.value.title,
      category: form.value.category,
      meeting_date: formattedDate, // Date 타입 매핑
      meeting_time: formattedTime, // Time 타입 매핑
      location_name: form.value.location, // location_name 매핑
      max_participants: Number(form.value.max), // Integer 타입 변환
      content: form.value.description || "", // content 매핑 (contentText 아님!)
      password: form.value.password,
      location_id: form.value.location_id || null, // 공공데이터 연동 ID
    };

    // 4. API 전송 실행 (api.js의 axios.post 호출)
    await createMeeting(backendPayload);
    submitted.value = true;

    // 성공 시 모임 목록 화면으로 이동
    setTimeout(() => router.push("/meetings"), 1200);
  } catch (error) {
    console.error("모임 생성 실패 디버깅 로그:", error);
    alert("모임 등록 규격이 올바르지 않습니다. 다시 시도해 주세요!");
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-6 py-10">
    <h1 class="mb-6 text-3xl font-bold text-ink">모임 만들기</h1>

    <p v-if="submitted" class="mb-6 rounded-lg bg-brand-light px-4 py-3 text-brand-hover">
      모임이 등록되었어요! 목록으로 이동합니다...
    </p>

    <div class="space-y-5 rounded-xl border border-line bg-white p-6">
      <div>
        <label class="field-label">제목 *</label>
        <input
          v-model="form.title"
          type="text"
          required
          class="field-input"
          placeholder="예: 오늘 저녁 알고리즘 모각코"
        />
      </div>

      <div>
        <label class="field-label">카테고리</label>
        <select v-model="form.category" class="field-input">
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="field-label">날짜 *</label>
          <input
            v-model="form.date"
            type="text"
            required
            class="field-input"
            placeholder="예: 오늘, 토요일"
          />
        </div>
        <div>
          <label class="field-label">시간 *</label>
          <input v-model="form.time" type="time" required class="field-input" />
        </div>
      </div>

      <div>
        <label class="field-label">장소 *</label>
        <input
          v-model="form.location"
          type="text"
          required
          class="field-input"
          placeholder="예: SSAFY 대전 캠퍼스 스터디룸 A"
        />
        <p v-if="form.location_id" class="mt-1.5 text-xs font-semibold text-brand-hover">
          📍 추천 장소 정보가 자동으로 안전하게 기입되었습니다.
        </p>
      </div>

      <div>
        <label class="field-label">최대 모집 인원 *</label>
        <input
          v-model.number="form.max"
          type="number"
          min="2"
          max="20"
          required
          class="field-input"
        />
      </div>

      <div>
        <label class="field-label">상세 내용</label>
        <textarea
          v-model="form.description"
          rows="4"
          class="field-input"
          placeholder="모임에 대해 자유롭게 소개해주세요."
        ></textarea>
      </div>

      <div>
        <label class="field-label">수정·삭제용 비밀번호 *</label>
        <input
          v-model="form.password"
          type="password"
          required
          class="field-input"
          placeholder="모임 관리를 위한 비밀번호"
        />
      </div>

      <button type="button" class="btn-primary w-full" @click="submit">모임 등록하기</button>
    </div>
  </div>
</template>
