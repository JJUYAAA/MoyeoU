<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import lightningIcon from "@/assets/lightning.svg";

const props = defineProps({
  meetings: {
    type: Array,
    default: () => [],
  },
  // 번개 온도 및 밀집도(클러스터러) 표시 여부를 결정하는 옵션
  isCluster: {
    type: Boolean,
    default: false,
  },
});

const mapContainer = ref(null);
let map = null;
let clusterer = null;
let renderedMarkers = [];

onMounted(() => {
  // index.html에서 autoload=false로 불러온 SDK가 있으면
  // 새로운 script를 추가하지 않고 load만 실행
  if (
    window.kakao &&
    window.kakao.maps
  ) {
    window.kakao.maps.load(initMap);
    return;
  }

  // SDK 자체가 없는 경우에만 새 script 추가
  const script =
    document.createElement("script");

  script.src =
    `//dapi.kakao.com/v2/maps/sdk.js` +
    `?autoload=false` +
    `&appkey=${import.meta.env.VITE_KAKAO_MAP_API_KEY}` +
    `&libraries=services,clusterer`;

  script.onload = () => {
    window.kakao.maps.load(initMap);
  };

  script.onerror = () => {
    console.error(
      "카카오 지도 SDK를 불러오지 못했습니다.",
    );
  };

  document.head.appendChild(script);
});

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

  const firstMeeting = props.meetings.find(
    (meeting) =>
      meeting.map_y !== null &&
      meeting.map_y !== undefined &&
      meeting.map_x !== null &&
      meeting.map_x !== undefined &&
      Number.isFinite(Number(meeting.map_y)) &&
      Number.isFinite(Number(meeting.map_x)),
  );

  const initialCenter =
    !props.isCluster && firstMeeting
      ? new window.kakao.maps.LatLng(
          Number(firstMeeting.map_y),
          Number(firstMeeting.map_x),
        )
      : campusLatLng;

  const options = {
    center: initialCenter,
    level: props.isCluster ? 4 : 3,
  };

  map = new window.kakao.maps.Map(container, options);

  // 홈 지도에서만 캠퍼스 기준 위치를 함께 표시
  if (props.isCluster) {
    const campusMarker = new window.kakao.maps.Marker({
      position: campusLatLng,
      map: map,
    });

    const campusInfoWindow = new window.kakao.maps.InfoWindow({
      position: campusLatLng,
      content: `<div style="padding:5px 10px;font-size:12px;font-weight:bold;color:#ef4444;text-align:center;">📍삼성화재 유성연수원</div>`,
    });
    campusInfoWindow.open(map, campusMarker);
  }

  // 클러스터링 모드가 활성화되어 있을 때만 클러스터러 인스턴스화
  if (props.isCluster) {
    clusterer = new window.kakao.maps.MarkerClusterer({
      map: map,
      averageCenter: true,
      minLevel: 3, // 마커들이 클러스터링(합쳐지는) 최소 지도 축척 레벨
      styles: [
        {
          width: "55px",
          height: "55px",
          background:
            "radial-gradient(circle, rgba(239, 68, 68, 0.95) 0%, rgba(220, 38, 38, 0.85) 100%)",
          borderRadius: "50%",
          color: "#fff",
          textAlign: "center",
          fontWeight: "black",
          fontSize: "14px",
          lineHeight: "55px",
          boxShadow: "0 0 0 8px rgba(239, 68, 68, 0.3), 0 4px 15px rgba(0,0,0,0.25)",
          animation: "pulse 2s infinite",
        },
      ],
    });
  }

  if (props.meetings && props.meetings.length > 0) {
    updateMarkers(props.meetings);
  }
};

const updateMarkers = (meetingsList) => {
  if (!map) return;

  // 클러스터러 및 기존 마커 초기화
  if (clusterer) {
    clusterer.clear();
  }
  renderedMarkers.forEach((marker) => marker.setMap(null));
  renderedMarkers = [];

  // 기존 latitude/longitude를 실제 데이터베이스 컬럼명인 map_y/map_x로 바인딩
  const markers = meetingsList
    .filter(
      (meeting) =>
        meeting.map_y !== null &&
        meeting.map_y !== undefined &&
        meeting.map_x !== null &&
        meeting.map_x !== undefined &&
        Number.isFinite(Number(meeting.map_y)) &&
        Number.isFinite(Number(meeting.map_x)),
    )
    .map((meeting) => {
      const imageSrc = lightningIcon;
      const imageSize = new window.kakao.maps.Size(40, 40);
      const imageOption = { offset: new window.kakao.maps.Point(20, 40) };

      const markerImage = new window.kakao.maps.MarkerImage(imageSrc, imageSize, imageOption);

      const marker = new window.kakao.maps.Marker({
        position: new window.kakao.maps.LatLng(meeting.map_y, meeting.map_x),
        image: markerImage,
      });

      const infowindow = new window.kakao.maps.InfoWindow({
        content: `<div style="padding:10px;font-size:12px;font-weight:600;min-width:150px;text-align:center;">${meeting.title}</div>`,
        removable: true,
      });

      window.kakao.maps.event.addListener(marker, "click", () => {
        infowindow.open(map, marker);
      });

      // 클러스터링 상태가 아니라면 마커를 지도 상에 즉시 직접 그림
      if (!props.isCluster) {
        marker.setMap(map);
      }

      return marker;
    });

  renderedMarkers = markers;

  // 상세 화면에서는 해당 모임 장소를 지도 중앙에 표시
  if (!props.isCluster && markers.length === 1) {
    map.setCenter(markers[0].getPosition());
  }

  // 클러스터링 모드가 활성화되어 있다면, 클러스터러에 마커를 통째로 집어넣어 합쳐 표기
  if (props.isCluster && clusterer) {
    clusterer.addMarkers(markers);
  }
};

watch(
  () => props.meetings,
  (newMeetings) => {
    if (newMeetings && newMeetings.length > 0) {
      updateMarkers(newMeetings);
    } else {
      if (clusterer) {
        clusterer.clear();
      }
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

/* 번개 온도 클러스터 서클을 부드럽게 펄스 효과 내는 애니메이션 추가 */
@keyframes pulse {
  0% {
    box-shadow:
      0 0 0 0 rgba(239, 68, 68, 0.5),
      0 4px 15px rgba(0, 0, 0, 0.25);
  }
  70% {
    box-shadow:
      0 0 0 12px rgba(239, 68, 68, 0),
      0 4px 15px rgba(0, 0, 0, 0.25);
  }
  100% {
    box-shadow:
      0 0 0 0 rgba(239, 68, 68, 0),
      0 4px 15px rgba(0, 0, 0, 0.25);
  }
}
</style>
