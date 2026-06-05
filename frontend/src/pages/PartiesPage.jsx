import { useEffect, useState } from 'react';
import { ClipboardList, Plus, Search, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState';
import PartyCard from '../components/PartyCard';
import PlaceSearchField from '../components/PlaceSearchField';
import RouteMapPreview from '../components/RouteMapPreview';

const INITIAL_SEARCH = {
  start_place: '',
  end_place: '',
  departure_time: '',
  status: 'recruiting',
};

export default function PartiesPage({ navigate }) {
  const [search, setSearch] = useState(INITIAL_SEARCH);
  const [selectedPlaces, setSelectedPlaces] = useState({ start: null, end: null });
  const [parties, setParties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadParties();
  }, []);

  const updateSearch = (key, value) => {
    setSearch((current) => ({ ...current, [key]: value }));
  };

  const handlePlaceSelect = (type, place) => {
    setSelectedPlaces((current) => ({ ...current, [type]: place }));
    setSearch((current) => ({ ...current, [`${type}_place`]: place.name }));
    setMessage('');
  };

  const loadParties = async () => {
    setLoading(true);
    setMessage('');
    try {
      const result = await api.parties({
        status: search.status || 'recruiting',
        page: 1,
        limit: 20,
      });
      setParties(result.parties || []);
    } catch (error) {
      setMessage(error.message || '파티 목록을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const params = cleanParams(search);
      const hasCondition = Boolean(params.start_place || params.end_place || params.departure_time);
      const result = hasCondition
        ? await api.searchParties({ ...params, page: 1, limit: 20 })
        : await api.parties({
          status: search.status || 'recruiting',
          page: 1,
          limit: 20,
        });
      setParties(result.parties || []);
    } catch (error) {
      setMessage(error.message || '조건 검색에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async () => {
    if (!search.start_place || !search.end_place || !search.departure_time) {
      setMessage('추천을 받으려면 출발지와 목적지를 선택하고 희망 출발 시간을 입력해 주세요.');
      return;
    }

    setLoading(true);
    setMessage('');
    try {
      const result = await api.recommendParties({
        start_place: search.start_place,
        end_place: search.end_place,
        departure_time: normalizeLocalDateTime(search.departure_time),
      });
      setParties(result.parties || []);
    } catch (error) {
      setMessage(error.message || '유사 파티 추천에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen-grid">
      <section className="screen-hero-card compact">
        <p className="eyebrow">Parties</p>
        <h1>파티 목록·검색</h1>
        <p>지도 기반 장소 검색으로 출발지와 목적지를 선택하고, 조건에 맞는 파티를 확인합니다.</p>
      </section>

      <section className="workspace-card">
        <div className="card-title row">
          <div>
            <p className="eyebrow">검색 조건</p>
            <h2>조건으로 검색하기</h2>
          </div>
          <button className="solid-button" type="button" onClick={() => navigate('/parties/new')}>
            <Plus size={18} />
            파티 생성하기
          </button>
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
            <label>
              <span>희망 출발 시간</span>
              <input
                type="datetime-local"
                value={search.departure_time}
                onChange={(event) => updateSearch('departure_time', event.target.value)}
              />
            </label>
            <label>
              <span>상태</span>
              <select value={search.status} onChange={(event) => updateSearch('status', event.target.value)}>
                <option value="recruiting">모집 중</option>
                <option value="matched">매칭 완료</option>
                <option value="canceled">취소</option>
                <option value="expired">출발시간 만료</option>
                <option value="completed">이용 완료</option>
              </select>
            </label>
            <button className="quiet-button" type="submit" disabled={loading}>
              <Search size={18} />
              검색
            </button>
            <button className="quiet-button" type="button" onClick={handleRecommend} disabled={loading}>
              <Sparkles size={18} />
              유사 추천
            </button>
          </div>
        </form>
        {message && <p className="error">{message}</p>}
      </section>

      <section className="workspace-card">
        <div className="card-title">
          <p className="eyebrow">결과</p>
          <h2>파티 목록</h2>
        </div>
        {parties.length > 0 ? (
          <div className="party-list">
            {parties.map((party) => (
              <PartyCard key={party.id} navigate={navigate} party={party} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={ClipboardList}
            title={loading ? '파티를 불러오는 중입니다' : '조건에 맞는 파티가 없습니다'}
            text="조건을 바꾸거나 새 파티를 만들어 보세요."
            action={<button className="solid-button" type="button" onClick={() => navigate('/parties/new')}><Plus size={18} /> 새 파티 만들어보기</button>}
          />
        )}
      </section>
    </div>
  );
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
