import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, Send } from 'lucide-react';
import { api, getPartyChatWebSocketUrl, getToken } from '../api/client';
import { formatWon } from '../components/PartyCard';

export default function ChatPage({ navigate, partyId, user }) {
  const socketRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [party, setParty] = useState(null);
  const [draft, setDraft] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('Waiting');
  const [error, setError] = useState('');

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setError('로그인 토큰이 없어 채팅에 연결할 수 없습니다.');
      return undefined;
    }

    let mounted = true;
    const loadMessages = async () => {
      try {
        const [messageResult, partyResult] = await Promise.all([
          api.messages(partyId),
          api.partyDetail(partyId),
        ]);
        if (mounted) {
          setMessages(readMessageItems(messageResult));
          setParty(normalizeParty(readPartyPayload(partyResult)));
        }
      } catch (apiError) {
        if (mounted) setError(apiError.message || '채팅 메시지를 불러오지 못했습니다.');
      }
    };

    loadMessages();

    const socket = new WebSocket(getPartyChatWebSocketUrl(partyId));
    socketRef.current = socket;
    setConnectionStatus('Connecting');

    socket.onopen = () => {
      if (mounted) setConnectionStatus('Live');
    };

    socket.onmessage = (event) => {
      try {
        const nextMessage = JSON.parse(event.data);
        setMessages((current) => [...current, normalizeMessage(nextMessage)]);
      } catch {
        setError('메시지 형식을 확인할 수 없습니다.');
      }
    };

    socket.onerror = () => {
      if (mounted) setError('채팅 WebSocket 연결 중 오류가 발생했습니다.');
    };

    socket.onclose = () => {
      if (mounted) setConnectionStatus('Closed');
    };

    return () => {
      mounted = false;
      socket.close();
    };
  }, [partyId]);

  const handleSubmit = (event) => {
    event.preventDefault();
    const content = draft.trim();
    if (!content) return;

    if (socketRef.current?.readyState !== WebSocket.OPEN) {
      setError('채팅 서버에 연결된 뒤 메시지를 보낼 수 있습니다.');
      return;
    }

    socketRef.current.send(JSON.stringify({ content }));
    setDraft('');
    setError('');
  };

  return (
    <div className="screen-grid">
      <section className="screen-hero-card compact">
        <button className="text-button back-button" type="button" onClick={() => navigate(`/parties/${partyId}`)}>
          <ArrowLeft size={17} />
          파티 상세로 돌아가기
        </button>
        <p className="eyebrow">Party Detail/Messages</p>
        <h1>파티 #{partyId}</h1>
        <div className="chat-hero-metrics">
          <span><strong>출발지</strong><em>{party?.start_place || '-'}</em></span>
          <span><strong>도착지</strong><em>{party?.end_place || '-'}</em></span>
          <span><strong>1인당 요금</strong><em>{formatWon(party?.per_person_fare)}</em></span>
          <span><strong>참여 인원</strong><em>{party ? `${party.current_members}/${party.max_members}명` : '-'}</em></span>
        </div>
      </section>

      <section className="workspace-card chat-panel">
        {error && <p className="error">{error}</p>}

        <div className="chat-thread" aria-live="polite">
          <div className="chat-panel-head">
            <span className={`screen-note chat-status ${connectionStatus.toLowerCase()}`}>{connectionStatus}</span>
          </div>
          {messages.length > 0 ? messages.map((message) => {
            const normalized = normalizeMessage(message);
            const isMine = String(normalized.user_id) === String(user?.id);
            return (
              <article className={isMine ? 'chat-message mine' : 'chat-message'} key={`${normalized.id}-${normalized.created_at}-${normalized.content}`}>
                <span>{normalized.user_name || (isMine ? '나' : '참여자')}</span>
                <p>{normalized.content}</p>
                <time>{formatChatTime(normalized.created_at)}</time>
              </article>
            );
          }) : (
            <p className="chat-empty">아직 주고받은 메시지가 없습니다.</p>
          )}
        </div>

        <form className="chat-input" onSubmit={handleSubmit}>
          <input
            placeholder="만남 장소, 도착 예정 시간 등을 입력하세요"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
          />
          <button className="solid-button" type="submit" disabled={!draft.trim()}>
            <Send size={17} />
            전송
          </button>
        </form>
      </section>
    </div>
  );
}

function readPartyPayload(result) {
  return result?.party || result?.data || result;
}

function normalizeParty(party) {
  if (!party) return null;
  const members = party.members || party.participants || party.party_members || [];
  return {
    ...party,
    start_place: party.start_place || party.startPlace || party.origin || '출발지 미정',
    end_place: party.end_place || party.endPlace || party.destination || '도착지 미정',
    current_members: party.current_members ?? members.length,
    max_members: party.max_members ?? party.capacity ?? 4,
    per_person_fare: party.per_person_fare ?? party.perPersonFare,
  };
}

function readMessageItems(result) {
  const items = result?.items || result?.messages || result?.data || result || [];
  return Array.isArray(items) ? items.map(normalizeMessage) : [];
}

function normalizeMessage(message) {
  return {
    ...message,
    id: message.id || message.message_id || `${message.user_id || message.user?.id || 'local'}-${message.created_at || message.timestamp || ''}`,
    user_id: message.user_id || message.user?.id || message.sender_id,
    user_name: message.user_name || message.user?.name || message.sender_name,
    content: message.content || message.message || '',
    created_at: message.created_at || message.timestamp || message.sent_at,
  };
}

function formatChatTime(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}
