import { useMemo, useState } from 'react';
import {
  Clock3,
  Plus,
  Search,
  Sparkles,
} from 'lucide-react';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState';
import PartyCard from '../components/PartyCard';
import PlaceSearchField from '../components/PlaceSearchField';
import RouteMapPreview from '../components/RouteMapPreview';

const INITIAL_CONDITION = {
  start_place: '',
  start_lat: '',
  start_lng: '',
  end_place: '',
  end_lat: '',
  end_lng: '',
  departure_time: getDefaultDepartureTime(),
};

export default function MainPage({ navigate, user }) {
  const [condition, setCondition] = useState(INITIAL_CONDITION);
  const [selectedPlaces, setSelectedPlaces] = useState({ start: null, end: null });
  const [recommendations, setRecommendations] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const createUrl = useMemo(() => buildPartyCreateUrl(condition), [condition]);
  const listUrl = useMemo(() => buildPartiesUrl(condition), [condition]);

  const updateCondition = (key, value) => {
    setCondition((current) => ({ ...current, [key]: value }));
    setMessage('');
  };

  const handlePlaceSelect = (type, place) => {
    setSelectedPlaces((current) => ({ ...current, [type]: place }));
    setCondition((current) => ({
      ...current,
      [`${type}_place`]: place.name,
      [`${type}_lat`]: place.lat,
      [`${type}_lng`]: place.lng,
    }));
    setMessage('');
  };

  const handleRecommend = async (event) => {
    event.preventDefault();

    if (!condition.start_place || !condition.end_place || !condition.departure_time) {
      setMessage('출발지, 목적지, 희망 출발 시간을 모두 입력해 주세요.');
      return;
    }

    setLoading(true);
    setSearched(true);
    setMessage('');
    try {
      const result = await api.recommendParties({
        start_place: condition.start_place,
        end_place: condition.end_place,
        departure_time: normalizeLocalDateTime(condition.departure_time),
      });
      setRecommendations(readPartyItems(result));
    } catch (error) {
      setRecommendations([]);
      setMessage(error.message || '조건과 비슷한 파티를 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen-grid home-dashboard polished-home">
      <section className="screen-hero-card home-hero quickstart-hero">
        <div>
          <p className="eyebrow">Main Menu</p>
          <h1>{user?.name || '사용자'}님, 오늘의 이동을 시작해볼까요?</h1>
          <p>
            장소를 선택하고 출발 시간을 입력하면 빠르게 시작할 수 있습니다.
          </p>
        </div>
      </section>

      <section className="workspace-card quick-start-card polished-card">
        <p className="eyebrow quick-start-kicker">Quick Start</p>
        <form className="quick-start-grid" onSubmit={handleRecommend}>
          <div className="quick-start-fields">
            <div className="quick-route-label">
              <span>1</span>
              <strong>이동 경로</strong>
              <p>검색 결과를 선택하면 지도에서 출발지와 목적지가 함께 표시됩니다.</p>
            </div>
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
            <div className="quick-route-label compact">
              <span>2</span>
              <strong>출발 시간</strong>
              <p>희망 출발 시간을 선택하면 추천 파티를 확인할 수 있습니다.</p>
            </div>
            <label className="time-field elevated-time-field">
              <span><Clock3 size={15} /> 희망 출발 시간</span>
              <input
                type="datetime-local"
                value={condition.departure_time}
                onChange={(event) => updateCondition('departure_time', event.target.value)}
              />
            </label>
          </div>

          <div className="quick-start-map refined-map-panel">
            <RouteMapPreview end={selectedPlaces.end} start={selectedPlaces.start} />
            <div className="quick-start-actions">
              <button className="solid-button magnetic-button" type="submit" disabled={loading}>
                <Sparkles size={18} />
                {loading ? '확인 중' : '빠른 시작'}
              </button>
              <button className="quiet-button magnetic-button" type="button" onClick={() => navigate('/parties')}>
                <Search size={18} />
                파티 목록
              </button>
            </div>
          </div>
        </form>

        {message && <p className="error">{message}</p>}

        {searched && (
          <div className="quickstart-result">
            {recommendations.length > 0 ? (
              <>
                <div className="card-title row">
                  <div>
                    <p className="eyebrow">추천 파티</p>
                    <h2>비슷한 조건의 파티가 있습니다.</h2>
                  </div>
                  <button className="quiet-button" type="button" onClick={() => navigate(listUrl)}>
                    조건으로 목록 조회
                  </button>
                </div>
                <div className="party-list">
                  {recommendations.map((party) => (
                    <PartyCard key={party.id} navigate={navigate} party={party} />
                  ))}
                </div>
              </>
            ) : (
              <EmptyState
                icon={Plus}
                title={loading ? '추천 파티를 불러오는 중입니다' : '추천 파티가 없습니다'}
                text={loading ? '입력한 조건과 비슷한 파티를 확인하고 있습니다.' : '이 조건으로 파티를 만드시겠습니까?'}
                action={(
                  <div className="action-row">
                    <button className="solid-button" type="button" onClick={() => navigate(createUrl)}>
                      <Plus size={18} />
                      파티 만들기
                    </button>
                    <button className="quiet-button" type="button" onClick={() => navigate(listUrl)}>
                      <Search size={18} />
                      조건으로 목록 조회
                    </button>
                  </div>
                )}
              />
            )}
          </div>
        )}
      </section>
    </div>
  );
}

function getDefaultDepartureTime() {
  const date = new Date(Date.now() + 60 * 60 * 1000);
  return formatLocalDateTime(date);
}

function formatLocalDateTime(date) {
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60 * 1000);
  return local.toISOString().slice(0, 16);
}

function buildPartiesUrl(condition) {
  const params = new URLSearchParams();
  Object.entries(condition).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const query = params.toString();
  return query ? `/parties?${query}` : '/parties';
}

function buildPartyCreateUrl(condition) {
  const params = new URLSearchParams();
  Object.entries(condition).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const query = params.toString();
  return query ? `/parties/new?${query}` : '/parties/new';
}

function normalizeLocalDateTime(value) {
  if (!value) return value;
  return value.length === 16 ? `${value}:00` : value;
}

function readPartyItems(result) {
  if (Array.isArray(result)) return result;
  if (Array.isArray(result?.parties)) return result.parties;
  if (Array.isArray(result?.items)) return result.items;
  if (Array.isArray(result?.data)) return result.data;
  return [];
}
