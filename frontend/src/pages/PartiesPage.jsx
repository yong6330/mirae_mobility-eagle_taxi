import { useEffect, useMemo, useState } from 'react';
import { ClipboardList, Plus, RotateCw, Search } from 'lucide-react';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState';
import PartyCard from '../components/PartyCard';
import PlaceSearchField from '../components/PlaceSearchField';
import RouteMapPreview from '../components/RouteMapPreview';

const INITIAL_SEARCH = {
  start_place: '',
  start_lat: '',
  start_lng: '',
  end_place: '',
  end_lat: '',
  end_lng: '',
  departure_time: '',
  status: '',
};

export default function PartiesPage({ navigate, route }) {
  const [search, setSearch] = useState(INITIAL_SEARCH);
  const [selectedPlaces, setSelectedPlaces] = useState({ start: null, end: null });
  const [parties, setParties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const nextSearch = readSearchFromQuery();
    setSearch(nextSearch);
    setSelectedPlaces(readPlacesFromQuery(nextSearch));

    if (new URLSearchParams(window.location.search).get('mode') === 'recommend' && canRecommend(nextSearch)) {
      loadRecommendedParties(nextSearch);
      return;
    }

    loadBrowseParties(nextSearch.status);
  }, [route]);

  const createUrl = useMemo(() => buildPartyCreateUrl(search), [search]);

  const updateSearch = (key, value) => {
    setSearch((current) => ({ ...current, [key]: value }));
  };

  const handlePlaceSelect = (type, place) => {
    setSelectedPlaces((current) => ({ ...current, [type]: place }));
    setSearch((current) => ({
      ...current,
      [`${type}_place`]: place.name,
      [`${type}_lat`]: place.lat,
      [`${type}_lng`]: place.lng,
    }));
    setMessage('');
  };

  const loadBrowseParties = async (status = '') => {
    setLoading(true);
    setMessage('');
    try {
      const params = { page: 1, limit: 30 };
      if (status) params.status = status;
      const result = await api.parties(params);
      setParties(readPartyItems(result));
    } catch (error) {
      setParties([]);
      setMessage(error.message || '파티 목록을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (event) => {
    event.preventDefault();
    const params = cleanParams(search);
    const hasCondition = Boolean(params.start_place || params.end_place || params.departure_time || params.status);

    if (!hasCondition) {
      await loadBrowseParties('');
      return;
    }

    setLoading(true);
    setMessage('');
    try {
      const result = await api.searchParties({ ...params, page: 1, limit: 30 });
      setParties(readPartyItems(result));
    } catch (error) {
      setParties([]);
      setMessage(error.message || '조건 검색에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendedParties = async (values) => {
    setLoading(true);
    setMessage('');
    try {
      const result = await api.recommendParties({
        start_place: values.start_place,
        end_place: values.end_place,
        departure_time: normalizeLocalDateTime(values.departure_time),
      });
      setParties(readPartyItems(result));
    } catch (error) {
      setParties([]);
      setMessage(error.message || '유사 파티 추천에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const resetToBrowse = () => {
    setSearch(INITIAL_SEARCH);
    setSelectedPlaces({ start: null, end: null });
    loadBrowseParties('');
    navigate('/parties');
  };

  return (
    <div className="screen-grid parties-screen">
      <section className="screen-hero-card compact party-list-hero">
        <div>
          <p className="eyebrow">Party List</p>
          <h1>파티 목록</h1>
        </div>
        <div className="browse-actions">
          <button className="quiet-button" type="button" onClick={() => loadBrowseParties(search.status)} disabled={loading}>
            <RotateCw size={18} />
            새로 고침
          </button>
          <button className="solid-button" type="button" onClick={() => navigate('/parties/new')}>
            <Plus size={18} />
            파티 생성
          </button>
        </div>
      </section>

      <section className="workspace-card">
        <div className="card-title row">
          <div>
            <p className="eyebrow">Filter</p>
            <h2>장소와 시간을 입력해 주세요!</h2>
          </div>
        </div>
        <form className="party-filter-form" onSubmit={handleSearch}>
          <div className="party-filter-grid">
            <div className="search-location-stack">
              <PlaceSearchField
                label="출발지"
                placeholder="예: 연세대학교 미래캠퍼스"
                selectedPlace={selectedPlaces.start}
                type="start"
                onSelect={handlePlaceSelect}
              />
              <PlaceSearchField
                label="목적지"
                placeholder="예: 원주역"
                selectedPlace={selectedPlaces.end}
                type="end"
                onSelect={handlePlaceSelect}
              />
            </div>
            <RouteMapPreview end={selectedPlaces.end} start={selectedPlaces.start} />
          </div>

          <div className="condition-form search-controls">
            <label className="time-field">
              <span>출발 시간</span>
              <input
                type="datetime-local"
                value={search.departure_time}
                onChange={(event) => updateSearch('departure_time', event.target.value)}
              />
            </label>
            <label>
              <span>상태</span>
              <select value={search.status} onChange={(event) => updateSearch('status', event.target.value)}>
                <option value="">전체 상태</option>
                <option value="recruiting">모집 중</option>
                <option value="matched">매칭 완료</option>
                <option value="canceled">취소</option>
                <option value="expired">출발시간 만료</option>
                <option value="completed">이용 완료</option>
              </select>
            </label>
            <button className="quiet-button" type="submit" disabled={loading}>
              <Search size={18} />
              조건 검색
            </button>
            <button className="quiet-button" type="button" onClick={resetToBrowse} disabled={loading}>
              <RotateCw size={18} />
              조건 초기화
            </button>
          </div>
        </form>
        {message && <p className="error">{message}</p>}
      </section>

      <section className="workspace-card">
        {parties.length > 0 ? (
          <div className="party-list">
            {parties.map((party) => (
              <PartyCard key={party.id} navigate={navigate} party={party} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={ClipboardList}
            title={loading ? '파티를 불러오는 중입니다' : '표시할 파티가 없습니다'}
            text="조건을 바꾸거나 지금 바로 새 파티를 만들어 보세요."
            action={(
              <button className="solid-button" type="button" onClick={() => navigate(createUrl)}>
                <Plus size={18} />
                새 파티 만들기
              </button>
            )}
          />
        )}
      </section>
    </div>
  );
}

function readSearchFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return {
    ...INITIAL_SEARCH,
    start_place: params.get('start_place') || '',
    start_lat: params.get('start_lat') || '',
    start_lng: params.get('start_lng') || '',
    end_place: params.get('end_place') || '',
    end_lat: params.get('end_lat') || '',
    end_lng: params.get('end_lng') || '',
    departure_time: params.get('departure_time') || '',
    status: params.get('status') || '',
  };
}

function readPlacesFromQuery(search) {
  return {
    start: buildPlaceFromSearch(search, 'start', '빠른 시작에서 선택한 출발지'),
    end: buildPlaceFromSearch(search, 'end', '빠른 시작에서 선택한 목적지'),
  };
}

function buildPlaceFromSearch(search, type, address) {
  const name = search[`${type}_place`];
  const latValue = search[`${type}_lat`];
  const lngValue = search[`${type}_lng`];
  const lat = Number(latValue);
  const lng = Number(lngValue);
  if (!name || !latValue || !lngValue || !Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  return { name, address, lat, lng };
}

function cleanParams(values) {
  return Object.fromEntries(
    Object.entries({
      ...values,
      departure_time: normalizeLocalDateTime(values.departure_time),
    }).filter(([, value]) => value !== ''),
  );
}

function normalizeLocalDateTime(value) {
  if (!value) return value;
  return value.length === 16 ? `${value}:00` : value;
}

function canRecommend(values) {
  return Boolean(values.start_place && values.end_place && values.departure_time);
}

function readPartyItems(result) {
  if (Array.isArray(result)) return result;
  if (Array.isArray(result?.parties)) return result.parties;
  if (Array.isArray(result?.items)) return result.items;
  if (Array.isArray(result?.data)) return result.data;
  return [];
}

function buildPartyCreateUrl(condition) {
  const params = new URLSearchParams();
  Object.entries(condition).forEach(([key, value]) => {
    if (value && key !== 'status') params.set(key, value);
  });
  const query = params.toString();
  return query ? `/parties/new?${query}` : '/parties/new';
}
