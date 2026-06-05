import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, MessageCircle, Send } from 'lucide-react';
import { api, getPartyChatWebSocketUrl, getToken } from '../api/client';
import EmptyState from '../components/EmptyState';

export default function ChatPage({ navigate, partyId, user }) {
  const socketRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('대기 중');
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
        const result = await api.messages(partyId);
        if (mounted) setMessages(result.items || []);
      } catch (apiError) {
        if (mounted) setError(apiError.message || '채팅 메시지를 불러오지 못했습니다.');
      }
    };

    loadMessages();

    const socket = new WebSocket(getPartyChatWebSocketUrl(partyId));
    socketRef.current = socket;
    setConnectionStatus('연결 중');

    socket.onopen = () => {
      if (mounted) setConnectionStatus('실시간 연결됨');
    };

    socket.onmessage = (event) => {
      try {
        const nextMessage = JSON.parse(event.data);
        setMessages((current) => [...current, nextMessage]);
      } catch {
        // WebSocket payload must be JSON by backend spec. Ignore malformed payloads.
      }
    };

    socket.onerror = () => {
      if (mounted) setError('채팅 WebSocket 연결 중 오류가 발생했습니다.');
    };

    socket.onclose = () => {
      if (mounted) setConnectionStatus('연결 종료');
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
        <p className="eyebrow">Party Chat</p>
        <h1>파티 채팅</h1>
        <p>파티 참여자만 접근할 수 있는 실시간 대화 화면입니다.</p>
      </section>

      <section className="workspace-card chat-panel">
        <div className="card-title row">
          <div>
            <p className="eyebrow">Chat Room</p>
            <h2>실시간 메시지</h2>
          </div>
          <span className="screen-note">{connectionStatus}</span>
        </div>

        {error && <p className="error">{error}</p>}

        {messages.length > 0 ? (
          <div className="chat-thread" aria-live="polite">
            {messages.map((message) => {
              const isMine = String(message.user_id) === String(user?.id);
              return (
                <article className={isMine ? 'chat-message mine' : 'chat-message'} key={`${message.id}-${message.created_at}`}>
                  <span>{message.user_name || (isMine ? '나' : '참여자')}</span>
                  <p>{message.content}</p>
                  <time>{formatChatTime(message.created_at)}</time>
                </article>
              );
            })}
          </div>
        ) : (
          <EmptyState
            icon={MessageCircle}
            title="표시할 메시지가 없습니다"
            text="아직 주고받은 메시지가 없습니다."
          />
        )}

        <form className="chat-input" onSubmit={handleSubmit}>
          <input
            placeholder="메시지를 입력하세요"
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

function formatChatTime(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}
