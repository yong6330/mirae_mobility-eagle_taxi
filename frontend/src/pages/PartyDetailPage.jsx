import { useEffect, useMemo, useState } from 'react';
import {
  ArrowLeft,
  Ban,
  Clock3,
  LogOut,
  MapPin,
  MessageCircle,
  ShieldAlert,
  UserPlus,
  Users,
  WalletCards,
} from 'lucide-react';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState';
import RouteMapPreview from '../components/RouteMapPreview';
import { formatDateTime, formatStatus, formatWon } from '../components/PartyCard';

export default function PartyDetailPage({ navigate, partyId, user }) {
  const [party, setParty] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadPartyDetail();
  }, [partyId]);

  const isCreator = useMemo(() => {
    if (!party || !user) return false;
    const currentUserId = getUserId(user);
    return (
      sameId(party.creator_id, currentUserId)
      || sameId(party.creator?.id, currentUserId)
      || Boolean(party.creator?.email && user.email && party.creator.email === user.email)
    );
  }, [party, user]);

  const isMember = useMemo(() => {
    if (!party || !user) return false;
    const currentUserId = getUserId(user);
    return (
      sameId(party.creator_id, currentUserId)
      || sameId(party.creator?.id, currentUserId)
      || (party.members || []).some((member) => (
        sameId(member.user?.id, currentUserId)
      || sameId(member.user_id, currentUserId)
      || sameId(member.id, currentUserId)
      || Boolean(member.user?.email && user.email && member.user.email === user.email)
      || Boolean(member.email && user.email && member.email === user.email)
      ))
    );
  }, [party, user]);

  const canJoin = party?.status === 'recruiting' && !isMember;
  const canLeave = party?.status === 'recruiting' && isMember && !isCreator;
  const canCancel = ['recruiting', 'matched'].includes(party?.status) && isCreator;

  const loadPartyDetail = async () => {
    setLoading(true);
    setMessage('');
    try {
      const result = await api.partyDetail(partyId);
      setParty(normalizeParty(readPartyPayload(result)));
    } catch (error) {
      setParty(null);
      setMessage(resolveErrorMessage(error, '파티 정보를 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = async () => {
    setLoading(true);
    setMessage('');
    try {
      const result = await api.joinParty(partyId);
      setParty(normalizeParty(readPartyPayload(result)));
      setMessage('파티에 참여했습니다.');
    } catch (error) {
      setMessage(resolveErrorMessage(error, '파티 참여에 실패했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  const handleLeave = async () => {
    if (!window.confirm('이 파티 참여를 취소할까요?')) return;
    setLoading(true);
    setMessage('');
    try {
      const result = await api.leaveParty(partyId);
      setParty(normalizeParty(readPartyPayload(result)));
      setMessage('파티 참여를 취소했습니다.');
    } catch (error) {
      setMessage(resolveErrorMessage(error, '참여 취소에 실패했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    const confirmMsg = party?.status === 'matched'
      ? '파티가 매칭 완료 상태입니다. 모든 참여자의 합승이 취소됩니다. 정말 취소할까요?'
      : '생성한 파티를 취소할까요?';
    if (!window.confirm(confirmMsg)) return;
    setLoading(true);
    setMessage('');
    try {
      const result = await api.cancelParty(partyId, { cancel_reason: '생성자 취소' });
      setParty(normalizeParty(readPartyPayload(result)));
      setMessage('파티가 취소되었습니다.');
    } catch (error) {
      setMessage(resolveErrorMessage(error, '파티 취소에 실패했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  const mapStart = party
    ? { name: party.start_place, lat: party.start_lat, lng: party.start_lng }
    : null;
  const mapEnd = party
    ? { name: party.end_place, lat: party.end_lat, lng: party.end_lng }
    : null;

  return (
    <div className="screen-grid">
      <section className="screen-hero-card compact">
        <button className="text-button back-button" type="button" onClick={() => navigate('/parties')}>
          <ArrowLeft size={17} />
          파티 목록으로 돌아가기
        </button>
        <p className="eyebrow">Party Detail</p>
        <h1>파티 상세</h1>
        <p>{party ? `${party.start_place}에서 ${party.end_place}까지 함께 이동하는 파티입니다.` : `partyId: ${partyId}`}</p>
      </section>

      {message && <p className={message.includes('실패') || message.includes('못했습니다') ? 'error' : 'success'}>{message}</p>}

      {!party ? (
        <section className="workspace-card">
          <EmptyState
            title={loading ? '파티 정보를 불러오는 중입니다' : '파티 정보를 불러올 수 없습니다'}
            text="파티 정보를 불러오면 출발지, 목적지, 시간, 참여자, 요금 정보가 표시됩니다."
          />
        </section>
      ) : (
        <>
          <section className="detail-grid">
            <article className="workspace-card">
              <div className="card-title">
                <span className={`status-badge status-${party.status}`}>{formatStatus(party.status)}</span>
                <h2>파티 정보</h2>
              </div>
              <div className="metric-list">
                <span><strong>출발지</strong><em>{party.start_place}</em></span>
                <span><strong>목적지</strong><em>{party.end_place}</em></span>
                <span><strong>희망 출발 시간</strong><em>{formatDateTime(party.departure_time)}</em></span>
                <span><strong>모집 인원</strong><em>{party.current_members}/{party.max_members}명</em></span>
                <span><strong>성별 매칭</strong><em>{formatGenderRule(party.gender_rule)}</em></span>
                <span><strong>만남 장소</strong><em>{party.meeting_point || '미정'}</em></span>
                <span><strong>만남 안내</strong><em>{party.meeting_note || '없음'}</em></span>
              </div>
            </article>

            <article className="workspace-card">
              <div className="card-title">
                <p className="eyebrow">Fare</p>
                <h2>요금 정보</h2>
              </div>
              <div className="metric-list">
                <span><strong>전체 예상 택시비</strong><em>{formatWon(party.estimated_fare)}</em></span>
                <span><strong>1인 예상 요금</strong><em>{formatWon(party.per_person_fare)}</em></span>
                <span><strong>예상 통행료</strong><em>{formatWon(party.toll_fare)}</em></span>
                <span><strong>예상 이동 거리</strong><em>{formatDistance(party.distance_meters)}</em></span>
                <span><strong>예상 이동 시간</strong><em>{formatDuration(party.duration_seconds)}</em></span>
              </div>
            </article>
          </section>

          <section className="workspace-card">
            <div className="card-title">
              <p className="eyebrow">Map</p>
              <h2>출발지·도착지 지도</h2>
            </div>
            <RouteMapPreview start={mapStart} end={mapEnd} />
          </section>

          <section className="detail-grid">
            <article className="workspace-card">
              <div className="card-title">
                <p className="eyebrow">Members</p>
                <h2>참여자</h2>
              </div>
              {(party.members || []).length > 0 ? (
                <div className="member-list">
                  {party.members.map((member, index) => (
                    <article className="member-card" key={getMemberKey(party.id, member, index)}>
                      <div>
                        <strong>{formatMemberName(member)}</strong>
                        <span>{formatMemberJoinedAt(member)}</span>
                      </div>
                      <em>참여 중</em>
                    </article>
                  ))}
                </div>
              ) : (
                <EmptyState title="참여자가 없습니다" text="파티에 참여하면 이 영역에 표시됩니다." />
              )}
            </article>

            <article className="workspace-card">
              <div className="card-title">
                <p className="eyebrow">Actions</p>
                <h2>파티 관리</h2>
              </div>
              <div className="action-row">
                <button className="solid-button" type="button" onClick={handleJoin} disabled={!canJoin || loading}>
                  <UserPlus size={18} />
                  참여하기
                </button>
                <button className="quiet-button" type="button" onClick={handleLeave} disabled={!canLeave || loading}>
                  <LogOut size={18} />
                  참여 취소
                </button>
                <button className="quiet-button" type="button" onClick={handleCancel} disabled={!canCancel || loading}>
                  <Ban size={18} />
                  파티 취소
                </button>
                <button className="quiet-button" type="button" onClick={() => navigate(`/parties/${partyId}/chat`)} disabled={!isMember}>
                  <MessageCircle size={18} />
                  채팅하기
                </button>
                <button
                  className="quiet-button"
                  type="button"
                  onClick={() => navigate(`/support?kind=report&party_id=${partyId}`)}
                >
                  <ShieldAlert size={18} />
                  신고하기
                </button>
              </div>
              <p className="helper-text">
                생성자는 파티를 취소할 수 있고, 참여자는 본인이 참여한 파티에서 나갈 수 있습니다.
              </p>
            </article>
          </section>

          <section className="workspace-card action-row">
            <span className="notice-box"><MapPin size={18} /> 실제 택시 호출은 제공하지 않습니다.</span>
            <span className="notice-box"><ShieldAlert size={18} /> 불편 사항은 신고하기로 접수할 수 있습니다.</span>
            <span className="notice-box"><WalletCards size={18} /> 요금은 예상 금액이며 실제 결제 금액과 다를 수 있습니다.</span>
          </section>
        </>
      )}
    </div>
  );
}

function formatGenderRule(value) {
  const labels = {
    any: '제한 없음',
    same_gender: '동성 매칭',
  };
  return labels[value] || value || '제한 없음';
}

function formatDistance(value) {
  if (value === null || value === undefined) return '계산 전';
  return `${(Number(value) / 1000).toLocaleString('ko-KR', { maximumFractionDigits: 1 })} km`;
}

function formatDuration(value) {
  if (value === null || value === undefined) return '계산 전';
  return `${Math.round(Number(value) / 60).toLocaleString('ko-KR')}분`;
}

function getUserId(user) {
  return user?.id ?? user?.user_id ?? user?.userId ?? null;
}

function sameId(left, right) {
  return left !== null && left !== undefined && right !== null && right !== undefined && String(left) === String(right);
}

function readPartyPayload(result) {
  return result?.party || result?.data || result;
}

function normalizeParty(party) {
  if (!party) return party;
  const members = party.members || party.participants || party.party_members || [];
  return {
    ...party,
    start_place: party.start_place || party.startPlace || party.origin || '출발지 미정',
    end_place: party.end_place || party.endPlace || party.destination || '목적지 미정',
    departure_time: party.departure_time || party.departure_at || party.departureTime || party.start_time,
    meeting_point: party.meeting_point || party.meetingPoint,
    meeting_note: party.meeting_note || party.meetingNote,
    current_members: party.current_members ?? members.length,
    max_members: party.max_members ?? party.capacity ?? 4,
    per_person_fare: party.per_person_fare ?? party.perPersonFare,
    members: members.map((member) => ({
      ...member,
      user: member.user || member.member || {
        id: member.user_id || member.id,
        name: member.user_name || member.name,
        email: member.user_email || member.email,
      },
      joined_at: member.joined_at || member.created_at || member.joinedAt,
    })),
  };
}

function getMemberKey(partyId, member, index) {
  return `${partyId}-${member.user?.id || member.user_id || member.user?.email || index}-${member.joined_at || 'joined'}`;
}

function formatMemberName(member) {
  return member.user?.name || member.name || member.user?.email || member.email || '참여자';
}

function formatMemberJoinedAt(member) {
  const value = member.joined_at || member.created_at;
  return value ? `${formatDateTime(value)} 참여` : '참여 시간 확인 중';
}

/** 에러 코드(error_code)가 있으면 사용자 친화적 메시지로, 없으면 fallback 사용. */
function resolveErrorMessage(error, fallback) {
  const codeMessages = {
    PARTY_FULL: '파티 인원이 꽉 찼습니다.',
    PARTY_TIME_OVERLAP: '같은 시간대에 이미 참여 중인 파티가 있습니다.',
    PARTY_GENDER_MISMATCH: '성별 매칭 조건에 맞지 않습니다.',
    PARTY_ALREADY_MEMBER: '이미 참여 중인 파티입니다.',
    PARTY_NOT_MEMBER: '해당 파티의 참여자가 아닙니다.',
    PARTY_NOT_FOUND: '파티를 찾을 수 없습니다.',
    PARTY_CANCELLED: '이미 취소된 파티입니다.',
    PARTY_COMPLETED: '이미 완료된 파티입니다.',
    PARTY_STATUS_INVALID: '현재 파티 상태에서는 해당 작업을 수행할 수 없습니다.',
    PARTY_NOT_OWNER: '파티 생성자만 이 작업을 수행할 수 있습니다.',
    AUTH_REQUIRED: '로그인이 필요합니다.',
    AUTH_FORBIDDEN: '권한이 없습니다.',
  };
  if (error?.errorCode && codeMessages[error.errorCode]) {
    return codeMessages[error.errorCode];
  }
  return error?.message || fallback;
}
