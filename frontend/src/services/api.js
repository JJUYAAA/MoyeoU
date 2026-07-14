import axios from "axios";

// 배포 대비 환경변수 적용
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// 공공데이터 장소 목록 조회
export async function getLocations() {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/locations`);
    return res.data;
  } catch (error) {
    console.error("[API Error] getLocations 실패:", error);
    return []; // 에러 발생 시 빈 배열 반환하여 프론트 터짐 방지
  }
}

// 전체 모임 목록 조회
export async function getMeetings() {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/meetings`);
    return res.data;
  } catch (error) {
    console.error("[API Error] getMeetings 실패:", error);
    return [];
  }
}

// 특정 모임 상세 조회
export async function getMeetingById(id) {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/meetings/${id}`);
    return res.data;
  } catch (error) {
    console.error(`[API Error] getMeetingById (${id}) 실패:`, error);
    return null;
  }
}

// 새로운 모임 등록
export async function createMeeting(data) {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/meetings`, data);
    return res.data;
  } catch (error) {
    console.error("[API Error] createMeeting 실패:", error);
    throw error;
  }
}

// AI 챗봇 검색 통신 연동
export async function searchChat(query) {
  try {
    const res = await axios.post(`${API_BASE_URL}/api/chat`, { message: query });
    return res.data;
  } catch (error) {
    console.error("[API Error] searchChat 실패:", error);
    return {
      reply: "죄송합니다. 챗봇 서버와 통신 중 에러가 발생했습니다.",
      results: [],
    };
  }
}
