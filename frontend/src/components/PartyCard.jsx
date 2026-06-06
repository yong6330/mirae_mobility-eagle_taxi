import { Clock3, MapPin, Users, WalletCards } from 'lucide-react';

export default function PartyCard({ actions, navigate, party }) {
  const normalized = normalizePartyCard(party);
  return (
    <article className="party-card">
      <div className="party-card-head">
        <span>{formatStatus(normalized.status)}</span>
        {'match_score' in normalized && <em>{normalized.match_score}점 추천</em>}
      </div>
      <h3>{normalized.start_place} → {normalized.end_place}</h3>
      {normalized.meeting_point && (
        <p className="party-card-note">
          <MapPin size={15} />
          {normalized.meeting_point}
        </p>
      )}
      <div className="party-meta">
        <span><Clock3 size={15} /> {formatDateTime(normalized.departure_time)}</span>
        <span><Users size={15} /> {normalized.current_members}/{normalized.max_members}명</span>
        <span><WalletCards size={15} /> {formatWon(normalized.per_person_fare)} / 1인</span>
      </div>
      <div className="party-card-actions">
        <button className="quiet-button" type="button" onClick={() => navigate(`/parties/${normalized.id}`)}>
          상세보기
        </button>
        {actions}
      </div>
    </article>
  );
}

function normalizePartyCard(party) {
  return {
    ...party,
    id: party.id || party.party_id,
    start_place: party.start_place || party.startPlace || party.origin || '출발지 미정',
    end_place: party.end_place || party.endPlace || party.destination || '목적지 미정',
    departure_time: party.departure_time || party.departure_at || party.departureTime || party.start_time,
    current_members: party.current_members ?? party.member_count ?? party.members?.length ?? 0,
    max_members: party.max_members ?? party.capacity ?? 4,
    per_person_fare: party.per_person_fare ?? party.perPersonFare,
    meeting_point: party.meeting_point || party.meetingPoint,
  };
}

export function formatStatus(status) {
  const labels = {
    recruiting: '모집 중',
    matched: '매칭 완료',
    canceled: '취소',
    expired: '출발시간 만료',
    completed: '이용 완료',
  };
  return labels[status] || status || '상태 없음';
}

export function formatDateTime(value) {
  if (!value) return '시간 미정';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('ko-KR', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function formatWon(value) {
  if (value === null || value === undefined) return '계산 전';
  return `${Number(value).toLocaleString('ko-KR')}원`;
}
