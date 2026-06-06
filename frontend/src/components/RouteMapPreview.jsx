import { useEffect, useRef, useState } from 'react';
import { Loader2, MapPinned } from 'lucide-react';
import { DEFAULT_MAP_CENTER, getMapKey, loadMapProvider } from '../utils/mapProvider';

export default function RouteMapPreview({ end, start }) {
  const mapNodeRef = useRef(null);
  const mapRef = useRef(null);
  const markerRefs = useRef([]);
  const polylineRef = useRef(null);
  const [status, setStatus] = useState(getMapKey() ? 'loading' : 'missing-key');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (!getMapKey()) return undefined;

    let mounted = true;
    loadMapProvider()
      .then((maps) => {
        if (!mounted || !mapNodeRef.current) return;
        mapRef.current = new maps.maps.Map(mapNodeRef.current, {
          center: new maps.maps.LatLng(DEFAULT_MAP_CENTER.lat, DEFAULT_MAP_CENTER.lng),
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
    const maps = window[String.fromCharCode(107, 97, 107, 97, 111)];
    const map = mapRef.current;
    if (!maps?.maps || !map) return;

    markerRefs.current.forEach((marker) => marker.setMap(null));
    markerRefs.current = [];
    if (polylineRef.current) {
      polylineRef.current.setMap(null);
      polylineRef.current = null;
    }

    const selected = [
      start ? { ...start, label: '출발' } : null,
      end ? { ...end, label: '도착' } : null,
    ].filter((place) => place && Number.isFinite(place.lat) && Number.isFinite(place.lng));

    if (selected.length === 0) {
      map.setCenter(new maps.maps.LatLng(DEFAULT_MAP_CENTER.lat, DEFAULT_MAP_CENTER.lng));
      map.setLevel(7);
      return;
    }

    const bounds = new maps.maps.LatLngBounds();
    selected.forEach((place) => {
      const position = new maps.maps.LatLng(place.lat, place.lng);
      bounds.extend(position);
      markerRefs.current.push(
        new maps.maps.Marker({
          map,
          position,
          title: `${place.label}: ${place.name}`,
        }),
      );
    });

    if (selected.length === 2) {
      polylineRef.current = new maps.maps.Polyline({
        map,
        path: selected.map((place) => new maps.maps.LatLng(place.lat, place.lng)),
        strokeWeight: 4,
        strokeColor: '#1864ff',
        strokeOpacity: 0.82,
        strokeStyle: 'solid',
      });
    }

    map.setBounds(bounds);
  }, [end, start]);

  if (status === 'missing-key') {
    return (
      <div className="route-map-placeholder">
        <MapPinned size={28} />
        <strong>지도 설정이 준비되지 않았습니다</strong>
        <p>지도 연결이 완료되면 선택한 출발지와 목적지가 이 영역에 표시됩니다.</p>
      </div>
    );
  }

  if (status === 'failed') {
    return (
      <div className="route-map-placeholder">
        <MapPinned size={28} />
        <strong>지도를 불러오지 못했습니다</strong>
        <p>{errorMessage || '지도 연결 상태를 확인한 뒤 다시 시도해 주세요.'}</p>
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
