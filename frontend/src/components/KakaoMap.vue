<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import lightningIcon from "@/assets/lightning.svg";

const props = defineProps({
  meetings: {
    type: Array,
    default: () => [],
  },
});

const mapContainer = ref(null);
let map = null;
let clusterer = null;

onMounted(() => {
  // ⚡ [해결] 이미 카카오맵 객체가 로드되어 존재한다면, 굳이 load()를 부르지 않고 즉시 지도를 그립니다.
  if (window.kakao && window.kakao.maps && window.kakao.maps.Map) {
    initMap();
  } else {
    const script = document.createElement("script");
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${import.meta.env.VITE_KAKAO_MAP_API_KEY}&libraries=clusterer`;
    script.onload = () => {
      window.kakao.maps.load(initMap);
    };
    document.head.appendChild(script);
  }
});

// 페이지 전환 시 안전하게 클린업하여 메모리 누수 방지
onBeforeUnmount(() => {
  try {
    if (clusterer) {
      clusterer.clear();
      clusterer = null;
    }
    if (map) {
      map = null;
    }
  } catch (error) {
    console.error("지도를 정리하는 도중 오류가 발생했습니다:", error);
  }
});

const initMap = () => {
  const container = mapContainer.value;
  if (!container) return;

  // 대전 캠퍼스(삼성화재 유성연수원) 중심 좌표 정의
  const campusLatLng = new window.kakao.maps.LatLng(36.3553675622378, 127.298408300646);

  const options = {
    center: campusLatLng,
    level: 4,
  };

  map = new window.kakao.maps.Map(container, options);

  // 캠퍼스 위치 하이라이트 고정 마커 생성
  const campusMarker = new window.kakao.maps.Marker({
    position: campusLatLng,
    map: map,
  });

  // 캠퍼스 마커 위에 항상 떠 있는 말풍선 추가
  const campusInfoWindow = new window.kakao.maps.InfoWindow({
    position: campusLatLng,
    content: `<div style="padding:5px 10px;font-size:12px;font-weight:bold;color:#ef4444;text-align:center;">📍삼성화재 유성연수원</div>`,
  });
  campusInfoWindow.open(map, campusMarker);

  clusterer = new window.kakao.maps.MarkerClusterer({
    map: map,
    averageCenter: true,
    minLevel: 5,
    styles: [
      {
        width: "40px",
        height: "40px",
        background: "rgba(239, 68, 68, 0.85)",
        borderRadius: "50%",
        color: "#fff",
        textAlign: "center",
        fontWeight: "bold",
        lineHeight: "40px",
        boxShadow: "0 0 15px rgba(239, 68, 68, 0.6)",
      },
    ],
  });

  // 실제 데이터가 넘어왔다면 즉시 마커를 그려줍니다.
  if (props.meetings && props.meetings.length > 0) {
    updateMarkers(props.meetings);
  }
};

const updateMarkers = (meetingsList) => {
  if (!map || !clusterer) return;

  clusterer.clear();

  const markers = meetingsList
    .filter((m) => m.latitude && m.longitude)
    .map((meeting) => {
      const imageSrc = lightningIcon;
      const imageSize = new window.kakao.maps.Size(40, 40);
      const imageOption = { offset: new window.kakao.maps.Point(20, 40) };

      const markerImage = new window.kakao.maps.MarkerImage(imageSrc, imageSize, imageOption);

      const marker = new window.kakao.maps.Marker({
        position: new window.kakao.maps.LatLng(meeting.latitude, meeting.longitude),
        image: markerImage,
      });

      const infowindow = new window.kakao.maps.InfoWindow({
        content: `<div style="padding:10px;font-size:12px;font-weight:600;min-width:150px;text-align:center;">${meeting.title}</div>`,
        removable: true,
      });

      window.kakao.maps.event.addListener(marker, "click", () => {
        infowindow.open(map, marker);
      });

      return marker;
    });

  clusterer.addMarkers(markers);
};

// props.meetings의 변화를 실시간으로 감시하되, 지도가 초기화된 이후 안전하게 그리도록 조율
watch(
  () => props.meetings,
  (newMeetings) => {
    if (newMeetings && newMeetings.length > 0) {
      updateMarkers(newMeetings);
    } else {
      clusterer?.clear();
    }
  },
  { deep: true },
);
</script>

<template>
  <div
    class="w-full h-[350px] min-h-[350px] rounded-2xl border border-line overflow-hidden shadow-md flex-1"
  >
    <div ref="mapContainer" class="w-full h-full min-h-[350px]"></div>
  </div>
</template>

<style scoped>
div {
  overflow: hidden;
}
</style>
