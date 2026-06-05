import { useState } from 'react';
import { CheckCircle2, Loader2, Search } from 'lucide-react';
import { DEFAULT_MAP_CENTER, getKakaoMapKey, loadKakaoMaps } from '../utils/kakaoMaps';

export default function PlaceSearchField({ label, onSelect, placeholder, selectedPlace, type }) {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [notice, setNotice] = useState(getKakaoMapKey() ? '' : 'Kakao Maps JavaScript 키가 필요합니다.');

  const searchPlaces = async (event) => {
    event.preventDefault();
    const trimmed = keyword.trim();

    if (!trimmed) {
      setNotice('검색할 장소명을 입력해 주세요.');
      setResults([]);
      return;
    }

    setSearching(true);
    setNotice('');
    try {
      const kakao = await loadKakaoMaps();
      if (!kakao.maps?.services?.Places) {
        throw new Error('Kakao Places 서비스가 초기화되지 않았습니다. JavaScript 키의 Local/Places 서비스 설정을 확인해 주세요.');
      }

      const places = new kakao.maps.services.Places();
      const center = new kakao.maps.LatLng(DEFAULT_MAP_CENTER.lat, DEFAULT_MAP_CENTER.lng);

      const requestKeywordSearch = (options) =>
        new Promise((resolve) => {
          places.keywordSearch(
            trimmed,
            (data, status) => resolve({ data, status }),
            options,
          );
        });

      let response = await requestKeywordSearch({
        location: center,
        radius: 20000,
        sort: kakao.maps.services.SortBy.ACCURACY,
      });

      if (response.status !== kakao.maps.services.Status.OK) {
        response = await requestKeywordSearch({
          sort: kakao.maps.services.SortBy.ACCURACY,
        });
      }

      setSearching(false);
      if (response.status !== kakao.maps.services.Status.OK) {
        setResults([]);
        setNotice('검색 결과가 없습니다. 장소명을 조금 더 구체적으로 입력해 주세요.');
        return;
      }

      const parsed = response.data.slice(0, 6).map((item) => ({
        id: item.id,
        name: item.place_name,
        address: item.road_address_name || item.address_name || '주소 정보 없음',
        lat: Number(item.y),
        lng: Number(item.x),
      }));
      setResults(parsed);
    } catch (error) {
      setSearching(false);
      setResults([]);
      setNotice(error.message || '장소 검색을 사용할 수 없습니다.');
    }
  };

  const selectPlace = (place) => {
    setKeyword(place.name);
    setResults([]);
    setNotice('');
    onSelect(type, place);
  };

  return (
    <fieldset className="place-search-field">
      <legend>{label}</legend>
      <div className="place-search-row">
        <label>
          <span>장소명 검색</span>
          <input
            placeholder={placeholder}
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') searchPlaces(event);
            }}
          />
        </label>
        <button className="quiet-button" type="button" onClick={searchPlaces} disabled={searching}>
          {searching ? <Loader2 className="spin" size={18} /> : <Search size={18} />}
          검색
        </button>
      </div>

      {notice && <p className="field-notice">{notice}</p>}

      {results.length > 0 && (
        <div className="place-result-list">
          {results.map((place) => (
            <button key={`${type}-${place.id}`} type="button" onClick={() => selectPlace(place)}>
              <strong>{place.name}</strong>
              <span>{place.address}</span>
            </button>
          ))}
        </div>
      )}

      {selectedPlace && (
        <div className="selected-place">
          <CheckCircle2 size={18} />
          <div>
            <strong>{selectedPlace.name}</strong>
            <span>{selectedPlace.address}</span>
          </div>
        </div>
      )}
    </fieldset>
  );
}
