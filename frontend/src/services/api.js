// API 서비스 레이어
// 지금은 목업 데이터를 반환합니다.
// 나중에 FastAPI 백엔드가 준비되면 fetch/axios 호출로 교체하세요.
//
// 예시:
//   const BASE_URL = 'http://localhost:8000'
//   export async function getMeetings() {
//     const res = await fetch(`${BASE_URL}/meetings`)
//     return res.json()
//   }

import { meetings, locations } from '@/data/mockData'

// 실제 네트워크 요청처럼 보이도록 살짝 지연시키는 헬퍼
const delay = (ms = 200) => new Promise((resolve) => setTimeout(resolve, ms))

export async function getMeetings() {
  await delay()
  return [...meetings]
}

export async function getMeetingById(id) {
  await delay()
  return meetings.find((m) => m.id === Number(id)) || null
}

export async function createMeeting(data) {
  await delay()
  // 목업: 실제 저장 없이 새 객체만 반환합니다.
  const newMeeting = { id: Date.now(), current: 1, status: 'OPEN', ...data }
  console.log('[모여유] createMeeting (mock):', newMeeting)
  return newMeeting
}

export async function getLocations() {
  await delay()
  return [...locations]
}

export async function searchChat(query) {
  await delay(300)
  // 아주 단순한 키워드 매칭 기반 목업 검색입니다.
  const keywords = {
    모각코: '모각코·스터디',
    스터디: '모각코·스터디',
    알고리즘: 'CS·알고리즘',
    백준: 'CS·알고리즘',
    코테: 'CS·알고리즘',
    CS: 'CS·알고리즘',
    점심: '점심·저녁',
    저녁: '점심·저녁',
    밥: '점심·저녁',
    프로젝트: '프로젝트·팀원',
    팀원: '프로젝트·팀원',
    관통: '프로젝트·팀원',
    러닝: '운동·산책',
    운동: '운동·산책',
    산책: '운동·산책',
    취준: '취준·정보공유',
    면접: '취준·정보공유',
  }

  const matchedCategory = Object.keys(keywords).find((k) => query.includes(k))
  const results = matchedCategory
    ? meetings.filter((m) => m.category === keywords[matchedCategory])
    : meetings.filter(
        (m) => m.title.includes(query) || m.description.includes(query),
      )

  return {
    reply: results.length
      ? `"${query}" 관련해서 ${results.length}개의 모임을 찾았어요!`
      : `"${query}" 관련 모임을 찾지 못했어요. 다른 키워드로 검색해보세요.`,
    results,
  }
}
