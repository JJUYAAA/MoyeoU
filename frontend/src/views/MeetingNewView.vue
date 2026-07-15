<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createMeeting } from "@/services/api";

const route = useRoute();
const router = useRouter();

const categories = ["관광", "문화생활", "운동·산책", "맛집", "쇼핑", "여행"];

const form = ref({
  title: "",
  category: categories[0],
  date: "",
  time: "",
  location: "",
  max: 4,
  description: "",
  password: "",
  location_id: null,
});

const submitted = ref(false);
const validationError = ref("");

onMounted(() => {
  if (route.query.loc_name) {
    form.value.location = String(route.query.loc_name);
  }
  if (route.query.loc_id) {
    form.value.location_id = String(route.query.loc_id);
  }
});

async function submit() {
  validationError.value = "";

  if (
    !form.value.title.trim() ||
    !form.value.date ||
    !form.value.time ||
    !form.value.location.trim() ||
    !form.value.password
  ) {
    validationError.value = "필수 입력 항목(*)을 모두 채워주세요!";
    return;
  }

  if (form.value.password.length < 4) {
    validationError.value = "비밀번호는 최소 4자리 이상 설정해 주세요.";
    return;
  }

  try {
    let formattedDate = form.value.date;
    if (formattedDate === "오늘") {
      formattedDate = new Date().toISOString().split("T")[0];
    } else if (formattedDate === "내일") {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      formattedDate = tomorrow.toISOString().split("T")[0];
    } else {
      const dateReg = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateReg.test(formattedDate)) {
        validationError.value =
          "날짜 형식(YYYY-MM-DD)을 올바르게 기입해 주시거나 달력에서 선택해 주세요.";
        return;
      }
    }

    let formattedTime = form.value.time;
    if (formattedTime && formattedTime.split(":").length === 2) {
      formattedTime = `${formattedTime}:00`;
    }

    const backendPayload = {
      title: form.value.title,
      category: form.value.category,
      meeting_date: formattedDate,
      meeting_time: formattedTime,
      location_name: form.value.location,
      max_participants: Number(form.value.max),
      content: form.value.description || "",
      password: form.value.password,
      location_id: form.value.location_id || null,
    };

    await createMeeting(backendPayload);
    submitted.value = true;

    setTimeout(() => router.push("/"), 1200);
  } catch (error) {
    console.error("모임 생성 실패 디버깅 로그:", error);
    validationError.value =
      error.response?.data?.detail?.[0]?.msg ||
      "모임 등록에 실패했습니다. 입력 양식을 다시 확인해 주세요!";
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-6 py-10">
    <h1 class="mb-6 text-3xl font-bold text-ink">모임 만들기</h1>

    <p v-if="submitted" class="mb-6 rounded-lg bg-green-50 px-4 py-3 text-green-700 font-semibold">
      🎉 모임이 성공적으로 등록되었습니다! 목록으로 이동합니다...
    </p>

    <div class="space-y-5 rounded-xl border border-line bg-white p-6 shadow-sm">
      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink">제목 *</label>
        <input
          v-model="form.title"
          type="text"
          required
          class="field-input w-full p-2.5 border rounded-lg"
          placeholder="예: 주말에 삼겹살 맛집 같이 가실 분!"
        />
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink">카테고리</label>
        <select v-model="form.category" class="field-input w-full p-2.5 border rounded-lg bg-white">
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="field-label block text-sm font-semibold mb-1 text-ink">날짜 *</label>
          <input
            v-model="form.date"
            type="date"
            required
            class="field-input w-full p-2.5 border rounded-lg"
          />
        </div>
        <div>
          <label class="field-label block text-sm font-semibold mb-1 text-ink">시간 *</label>
          <input
            v-model="form.time"
            type="time"
            required
            class="field-input w-full p-2.5 border rounded-lg"
          />
        </div>
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink">장소 *</label>
        <input
          v-model="form.location"
          type="text"
          required
          class="field-input w-full p-2.5 border rounded-lg"
          placeholder="예: SSAFY 대전 캠퍼스 주변 식당"
        />
        <p v-if="form.location_id" class="mt-1.5 text-xs font-semibold text-emerald-600">
          추천 장소 정보가 자동으로 안전하게 기입되었습니다. (ID: {{ form.location_id }})
        </p>
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink"
          >최대 모집 인원 *</label
        >
        <input
          v-model.number="form.max"
          type="number"
          min="2"
          max="100"
          required
          class="field-input w-full p-2.5 border rounded-lg"
        />
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink">상세 내용</label>
        <textarea
          v-model="form.description"
          rows="4"
          class="field-input w-full p-2.5 border rounded-lg"
          placeholder="모임에 대해 자유롭게 소개해주세요."
        ></textarea>
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink"
          >수정·삭제용 비밀번호 *</label
        >
        <input
          v-model="form.password"
          type="password"
          required
          class="field-input w-full p-2.5 border rounded-lg"
          placeholder="최소 4자리 이상의 비밀번호"
        />
      </div>

      <p v-if="validationError" class="text-sm font-semibold text-red-500">{{ validationError }}</p>

      <button
        type="button"
        class="btn-primary w-full bg-brand py-3 text-white font-bold rounded-lg hover:bg-brand/90"
        @click="submit"
      >
        모임 등록하기
      </button>
    </div>
  </div>
</template>
