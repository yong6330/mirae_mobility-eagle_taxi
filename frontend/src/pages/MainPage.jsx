import { useState } from 'react';
import { ClipboardList, Plus, Search, Sparkles, UserRoundCog } from 'lucide-react';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState';
import PartyCard from '../components/PartyCard';
import PlaceSearchField from '../components/PlaceSearchField';

const INITIAL_CONDITION = {
  start_place: '',
  start_lat: '',
  start_lng: '',
  end_place: '',
  end_lat: '',
  end_lng: '',
  departure_time: '',
};

export default function MainPage({ navigate, user }) {
  const [condition, setCondition] = useState(INITIAL_CONDITION);
  const [selectedPlaces, setSelectedPlaces] = useState({ start: null, end: null });
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [message, setMessage] = useState('');

  const updateCondition = (key, value) => {
    setCondition((current) => ({ ...current, [key]: value }));
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
    event?.preventDefault();

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
      setRecommendations(result.parties || []);
    } catch (error) {
      setRecommendations([]);
      setMessage(error.message || '유사 파티 추천에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const createUrl = buildPartyCreateUrl(condition);

  return (
    <div className="screen-grid">
      <section className="screen-hero-card">
        <p className="eyebrow">Main</p>
        <h1>{user?.name || '사용자'}님, 이동 조건을 입력해 유사 파티를 찾아보세요.</h1>
        <p>
          출발지와 목적지를 선택하고, 희망 출발 시간을 기준으로 모집 중인 파티를 추천받습니다.
        </p>
      </section>

      <section className="workspace-card">
        <div className="card-title row">
          <div>
            <p className="eyebrow">추천 조건 입력</p>
            <h2>장소명 검색 및 좌표 선택</h2>
          </div>
        </div>

        <form className="party-filter-form" onSubmit={handleRecommend}>
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

          <div className="condition-form main-search-controls">
            <label>
              <span>희망 출발 시간</span>
              <input
                type="datetime-local"
                value={condition.departure_time}
                onChange={(event) => updateCondition('departure_time', event.target.value)}
              />
            </label>
            <button className="solid-button" type="submit" disabled={loading}>
              <Search size={18} />
              검색하기
            </button>
          </div>
        </form>

        {message && <p className="error">{message}</p>}
      </section>

      <section className="workspace-card">
        <div className="card-title row">
          <div>
            <p className="eyebrow">추천 결과</p>
            <h2>유사 파티 추천</h2>
          </div>
          <button className="quiet-button" type="button" onClick={() => navigate('/parties')}>
            <Search size={18} />
            조건 검색으로 이동
          </button>
        </div>

        {recommendations.length > 0 ? (
          <div className="party-list">
            {recommendations.map((party) => (
              <PartyCard key={party.id} navigate={navigate} party={party} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={ClipboardList}
            title={loading ? '추천 파티를 불러오는 중입니다' : searched ? '조건에 맞는 추천 파티가 없습니다' : '추천 조건을 입력해 주세요'}
            text={
              searched
                ? '조건이 맞는 파티가 없으면 같은 조건으로 새 파티를 생성할 수 있습니다.'
                : '출발지와 목적지를 선택하고, 희망 출발 시간을 입력한 뒤 유사 파티 추천을 눌러 주세요.'
            }
            action={(
              <button className="solid-button" type="button" onClick={() => navigate(createUrl)}>
                <Plus size={18} />
                새 파티 만들기
              </button>
            )}
          />
        )}
      </section>

      <section className="quick-grid">
        <button type="button" onClick={handleRecommend} disabled={loading}><Sparkles size={20} /> 유사 파티 추천</button>
        <button type="button" onClick={() => navigate('/parties')}><Search size={20} /> 파티 목록</button>
        <button type="button" onClick={() => navigate(createUrl)}><Plus size={20} /> 파티 만들기</button>
        <button type="button" onClick={() => navigate('/my/parties')}><ClipboardList size={20} /> 내 파티</button>
        <button type="button" onClick={() => navigate('/settings')}><UserRoundCog size={20} /> 설정</button>
      </section>
    </div>
  );
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
