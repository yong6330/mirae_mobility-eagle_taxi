import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, CheckCircle2, Loader2, MapPin, Search, WalletCards } from 'lucide-react';
import { api } from '../api/client';
import { formatWon } from '../components/PartyCard';
import PlaceSearchField from '../components/PlaceSearchField';
import RouteMapPreview from '../components/RouteMapPreview';

const INITIAL_FORM = {
  start_place: '',
  start_lat: '',
  start_lng: '',
  end_place: '',
  end_lat: '',
  end_lng: '',
  departure_time: '',
  meeting_point: '',
  meeting_note: '',
  max_members: '4',
  gender_rule: 'any',
};

export default function PartyCreatePage({ navigate }) {
  const [form, setForm] = useState(() => readInitialFormFromQuery());
  const [places, setPlaces] = useState(() => readInitialPlacesFromQuery());
  const [estimate, setEstimate] = useState(null);
  const [estimating, setEstimating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const hasCoordinates = useMemo(
    () => Boolean(form.start_lat && form.start_lng && form.end_lat && form.end_lng),
    [form.end_lat, form.end_lng, form.start_lat, form.start_lng],
  );

  const hasValidEstimate = Boolean(estimate && estimate.fare_source !== 'fallback');

  const perPersonFare = useMemo(() => {
    if (!estimate) return null;
    const members = Number(form.max_members) || 1;
    return Math.ceil(Number(estimate.estimated_fare || 0) / members);
  }, [estimate, form.max_members]);

  const updateForm = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
    if (key === 'max_members') return;
    setEstimate(null);
  };

  const handlePlaceSelect = (type, place) => {
    setPlaces((current) => ({ ...current, [type]: place }));
    setForm((current) => ({
      ...current,
      [`${type}_place`]: place.name,
      [`${type}_lat`]: place.lat,
      [`${type}_lng`]: place.lng,
    }));
    setEstimate(null);
    setMessage('');
  };

  const requestEstimate = async ({ silent = false } = {}) => {
    if (!hasCoordinates) {
      if (!silent) setMessage('장소 검색 결과에서 출발지와 목적지를 먼저 선택해 주세요.');
      return null;
    }

    setEstimating(true);
    if (!silent) setMessage('');
    try {
      const result = await api.estimateFare({
        start_lat: form.start_lat,
        start_lng: form.start_lng,
        end_lat: form.end_lat,
        end_lng: form.end_lng,
      });
      setEstimate(result);
      if (result.fare_source === 'fallback') {
        setMessage('요금 산정에 실패해 백엔드가 fallback 값으로 응답했습니다. 문서 기준상 이 상태에서는 파티 생성을 진행하지 않습니다.');
      }
      return result;
    } catch (error) {
      setEstimate(null);
      setMessage(error.message || '예상 택시비 계산에 실패했습니다.');
      return null;
    } finally {
      setEstimating(false);
    }
  };

  useEffect(() => {
    if (!hasCoordinates) return undefined;

    let canceled = false;
    const timer = window.setTimeout(async () => {
      const result = await requestEstimate({ silent: true });
      if (!canceled && result?.fare_source === 'fallback') {
        setMessage('요금 산정에 실패해 백엔드가 fallback 값으로 응답했습니다. 문서 기준상 이 상태에서는 파티 생성을 진행하지 않습니다.');
      }
    }, 450);

    return () => {
      canceled = true;
      window.clearTimeout(timer);
    };
  }, [form.end_lat, form.end_lng, form.start_lat, form.start_lng, hasCoordinates]);

  const handleEstimate = async () => {
    await requestEstimate();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!hasCoordinates) {
      setMessage('장소 검색 결과에서 출발지와 목적지를 먼저 선택해 주세요.');
      return;
    }

    if (!form.departure_time) {
      setMessage('희망 출발 시간을 입력해 주세요.');
      return;
    }

    if (isPastLocalDateTime(form.departure_time)) {
      setMessage('출발 시간은 현재 이후 시간만 선택할 수 있습니다.');
      return;
    }

    if (Number(form.max_members) < 2 || Number(form.max_members) > 4) {
      setMessage('최대 인원은 2명 이상 4명 이하로 선택해 주세요.');
      return;
    }

    let fare = estimate;
    if (!fare) {
      fare = await requestEstimate({ silent: true });
    }
    if (!fare || fare.fare_source === 'fallback') {
      setMessage('예상 택시비를 계산하지 못해 파티를 생성할 수 없습니다. 백엔드 Kakao Mobility 설정을 확인해야 합니다.');
      return;
    }

    setSubmitting(true);
    setMessage('');

    try {
      const created = await api.createParty({
        start_place: form.start_place,
        start_lat: Number(form.start_lat),
        start_lng: Number(form.start_lng),
        end_place: form.end_place,
        end_lat: Number(form.end_lat),
        end_lng: Number(form.end_lng),
        departure_time: normalizeLocalDateTime(form.departure_time),
        meeting_point: form.meeting_point || null,
        meeting_note: form.meeting_note || null,
        max_members: Number(form.max_members),
        gender_rule: form.gender_rule,
      });
      navigate(`/parties/${created.id}`);
    } catch (error) {
      setMessage(error.message || '파티 생성에 실패했습니다.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="screen-grid two-column">
      <section className="workspace-card">
        <button className="text-button back-button" type="button" onClick={() => navigate('/parties')}>
          <ArrowLeft size={17} />
          파티 목록으로 돌아가기
        </button>
        <div className="card-title">
          <p className="eyebrow">Create Party</p>
          <h1>새 택시 파티 생성</h1>
          <p className="muted">
            장소명을 검색해 결과를 선택하면 좌표가 자동 저장되고, 선택된 좌표로 예상 택시비를 계산합니다.
          </p>
        </div>

        <form className="stack-form" onSubmit={handleSubmit}>
          <PlaceSearchField
            label="출발지"
            placeholder="예: 연세대학교 미래캠퍼스"
            selectedPlace={places.start}
            type="start"
            onSelect={handlePlaceSelect}
          />
          <PlaceSearchField
            label="목적지"
            placeholder="예: 원주역"
            selectedPlace={places.end}
            type="end"
            onSelect={handlePlaceSelect}
          />
          <label>
            <span>희망 출발 시간</span>
            <input
              type="datetime-local"
              value={form.departure_time}
              onChange={(event) => updateForm('departure_time', event.target.value)}
              required
            />
          </label>
          <label>
            <span>만남 장소</span>
            <input
              placeholder="예: 정문 택시 승강장"
              value={form.meeting_point}
              onChange={(event) => updateForm('meeting_point', event.target.value)}
            />
          </label>
          <label>
            <span>만남 안내</span>
            <textarea
              placeholder="파티원에게 전달할 안내를 입력하세요"
              value={form.meeting_note}
              onChange={(event) => updateForm('meeting_note', event.target.value)}
            />
          </label>
          <div className="inline-fields">
            <label>
              <span>최대 인원</span>
              <select value={form.max_members} onChange={(event) => updateForm('max_members', event.target.value)}>
                <option value="2">2명</option>
                <option value="3">3명</option>
                <option value="4">4명</option>
              </select>
            </label>
            <label>
              <span>성별 매칭</span>
              <select value={form.gender_rule} onChange={(event) => updateForm('gender_rule', event.target.value)}>
                <option value="any">제한 없음</option>
                <option value="same_gender">동성 매칭</option>
              </select>
            </label>
          </div>

          {message && <p className={message.includes('완료') ? 'success' : 'error'}>{message}</p>}

          <button className="solid-button full" type="submit" disabled={submitting || estimating}>
            {submitting ? '생성 중...' : '파티 생성하기'}
          </button>
        </form>
      </section>

      <aside className="workspace-card estimate-card">
        <RouteMapPreview end={places.end} start={places.start} />

        <div className="estimate-summary">
          <MapPin size={24} />
          <div>
            <h2>예상 택시비 자동 산정</h2>
            <p className="muted">
              출발지와 목적지를 선택하면 예상 요금을 자동 계산합니다.
            </p>
          </div>
        </div>
        <div className="metric-list">
          <span>
            <strong>전체 예상 택시비</strong>
            <em>{estimating ? '계산 중...' : formatWon(estimate?.estimated_fare)}</em>
          </span>
          <span>
            <strong>1인 예상 요금</strong>
            <em>{estimating ? '계산 중...' : formatWon(perPersonFare)}</em>
          </span>
          <span>
            <strong>예상 통행료</strong>
            <em>{estimating ? '계산 중...' : formatWon(estimate?.toll_fare)}</em>
          </span>
          <span>
            <strong>예상 이동 거리</strong>
            <em>{formatDistance(estimate?.distance_meters)}</em>
          </span>
          <span>
            <strong>예상 이동 시간</strong>
            <em>{formatDuration(estimate?.duration_seconds)}</em>
          </span>
          <span>
            <strong>요금 출처</strong>
            <em>{estimate?.fare_source || '계산 전'}</em>
          </span>
        </div>
        <button className="quiet-button full" type="button" onClick={handleEstimate} disabled={estimating}>
          {estimating ? <Loader2 className="spin" size={18} /> : <Search size={18} />}
          {estimating ? '계산 중...' : '예상 요금 다시 계산'}
        </button>
        <div className={hasValidEstimate ? 'notice-box' : 'notice-box warning'}>
          {hasValidEstimate ? <CheckCircle2 size={18} /> : <WalletCards size={18} />}
          {hasValidEstimate
            ? '요금 미리보기 계산이 완료되었습니다. 파티 생성 시 백엔드가 같은 좌표로 다시 계산합니다.'
            : '문서 기준상 예상 택시비 계산이 실패하면 파티 생성이 중단됩니다.'}
        </div>
      </aside>
    </div>
  );
}

function readInitialFormFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return {
    ...INITIAL_FORM,
    start_place: params.get('start_place') || '',
    start_lat: params.get('start_lat') || '',
    start_lng: params.get('start_lng') || '',
    end_place: params.get('end_place') || '',
    end_lat: params.get('end_lat') || '',
    end_lng: params.get('end_lng') || '',
    departure_time: params.get('departure_time') || '',
  };
}

function readInitialPlacesFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const start = buildPlaceFromQuery(params, 'start');
  const end = buildPlaceFromQuery(params, 'end');
  return { start, end };
}

function buildPlaceFromQuery(params, type) {
  const name = params.get(`${type}_place`);
  const lat = Number(params.get(`${type}_lat`));
  const lng = Number(params.get(`${type}_lng`));
  if (!name || !Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  return {
    id: `${type}-query`,
    name,
    address: '이전 화면에서 선택한 장소',
    lat,
    lng,
  };
}

function normalizeLocalDateTime(value) {
  if (!value) return value;
  return value.length === 16 ? `${value}:00` : value;
}

function isPastLocalDateTime(value) {
  if (!value) return false;
  const selected = new Date(value);
  return Number.isFinite(selected.getTime()) && selected.getTime() <= Date.now();
}

function formatDistance(value) {
  if (value === null || value === undefined) return '계산 전';
  if (value === 0) return '0 km';
  return `${(Number(value) / 1000).toFixed(1)} km`;
}

function formatDuration(value) {
  if (value === null || value === undefined) return '계산 전';
  if (value === 0) return '0분';
  return `${Math.round(Number(value) / 60)}분`;
}
