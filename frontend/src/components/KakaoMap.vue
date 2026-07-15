<script setup>
import { onMounted, ref } from "vue";
import lightningIcon from "@/assets/lightning.svg";

const mapContainer = ref(null);
let map = null;

const dummyMeetings = [
  { id: 1, title: "치맥할 SSAFY 동료 구함 🍗", lat: 36.3504, lng: 127.3845 },
  { id: 2, title: "알고리즘 모각코 하실 분 💻", lat: 36.3508, lng: 127.3852 },
];

onMounted(() => {
  if (window.kakao && window.kakao.maps) {
    window.kakao.maps.load(initMap);
  } else {
    const script = document.createElement("script");
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${import.meta.env.VITE_KAKAO_MAP_API_KEY}&libraries=clusterer`;
    script.onload = () => {
      window.kakao.maps.load(initMap);
    };
    document.head.appendChild(script);
  }
});

const initMap = () => {
  const container = mapContainer.value;
  if (!container) return;

  const options = {
    center: new window.kakao.maps.LatLng(36.3504, 127.3845),
    level: 4,
  };

  map = new window.kakao.maps.Map(container, options);

  const clusterer = new window.kakao.maps.MarkerClusterer({
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

  const markers = dummyMeetings.map((meeting) => {
    const imageSrc = lightningIcon;
    const imageSize = new window.kakao.maps.Size(40, 40);
    const imageOption = { offset: new window.kakao.maps.Point(20, 40) };

    const markerImage = new window.kakao.maps.MarkerImage(imageSrc, imageSize, imageOption);

    const marker = new window.kakao.maps.Marker({
      position: new window.kakao.maps.LatLng(meeting.lat, meeting.lng),
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
