import { useEffect, useRef, useState } from 'react';
import { Loader2, MapPinned } from 'lucide-react';
import { DEFAULT_MAP_CENTER, getKakaoMapKey, loadKakaoMaps } from '../utils/kakaoMaps';

export default function RouteMapPreview({ end, start }) {
  const mapNodeRef = useRef(null);
  const mapRef = useRef(null);
  const markerRefs = useRef([]);
  const [status, setStatus] = useState(getKakaoMapKey() ? 'loading' : 'missing-key');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (!getKakaoMapKey()) return undefined;

    let mounted = true;
    loadKakaoMaps()
      .then((kakao) => {
        if (!mounted || !mapNodeRef.current) return;
        mapRef.current = new kakao.maps.Map(mapNodeRef.current, {
          center: new kakao.maps.LatLng(DEFAULT_MAP_CENTER.lat, DEFAULT_MAP_CENTER.lng),
          level: 7,
        });
        setStatus('ready');
      })
      .catch((error) => {
        if (mounted) {
          setErrorMessage(error.message || '');
          setStatus('failed');
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const kakao = window.kakao;
    const map = mapRef.current;
    if (!kakao?.maps || !map) return;

    markerRefs.current.forEach((marker) => marker.setMap(null));
    markerRefs.current = [];

    const selected = [
      start ? { ...start, label: '출발' } : null,
      end ? { ...end, label: '도착' } : null,
    ].filter((place) => place && Number.isFinite(place.lat) && Number.isFinite(place.lng));

    if (selected.length === 0) {
      map.setCenter(new kakao.maps.LatLng(DEFAULT_MAP_CENTER.lat, DEFAULT_MAP_CENTER.lng));
      map.setLevel(7);
      return;
    }

    const bounds = new kakao.maps.LatLngBounds();
    selected.forEach((place) => {
      const position = new kakao.maps.LatLng(place.lat, place.lng);
      bounds.extend(position);
      markerRefs.current.push(
        new kakao.maps.Marker({
          map,
          position,
          title: `${place.label}: ${place.name}`,
        }),
      );
    });

    map.setBounds(bounds);
  }, [end, start]);

  if (status === 'missing-key') {
    return (
      <div className="route-map-placeholder">
        <MapPinned size={28} />
        <strong>Kakao Maps 키가 필요합니다</strong>
        <p>프론트 .env에 VITE_KAKAO_MAP_JS_KEY를 넣으면 장소 검색과 지도 핀이 동작합니다.</p>
      </div>
    );
  }

  if (status === 'failed') {
    return (
      <div className="route-map-placeholder">
        <MapPinned size={28} />
        <strong>지도를 불러오지 못했습니다</strong>
        <p>{errorMessage || 'Kakao Maps JavaScript 키와 허용 도메인을 확인해 주세요.'}</p>
      </div>
    );
  }

  return (
    <div className="route-map-shell">
      <div ref={mapNodeRef} className="route-map" />
      {status === 'loading' && (
        <div className="route-map-loading">
          <Loader2 className="spin" size={20} />
          지도를 불러오는 중
        </div>
      )}
    </div>
  );
}
