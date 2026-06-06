import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, CheckCircle2, MessageCircle, Plus, Send, ShieldAlert } from 'lucide-react';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState';

export default function SupportPage({ navigate, route }) {
  const routePreset = useMemo(() => readRoutePreset(route), [route]);
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [partyOptions, setPartyOptions] = useState([]);
  const [form, setForm] = useState(() => createInitialForm(routePreset));
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [composeMode, setComposeMode] = useState(true);

  useEffect(() => {
    setForm(createInitialForm(routePreset));
    setComposeMode(true);
    setSelectedThread(null);
  }, [routePreset.kind, routePreset.partyId]);

  useEffect(() => {
    loadSupportData();
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      loadSupportData({ silent: true });
    }, 7000);

    return () => window.clearInterval(timer);
  }, [selectedThread?.id, composeMode]);

  const selectedParty = partyOptions.find((party) => String(party.id) === String(form.party_id));

  const handleFormChange = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
    setMessage('');
  };

  const loadSupportData = async ({ silent = false } = {}) => {
    if (!silent) {
      setLoading(true);
      setMessage('');
    }
    try {
      const requests = [api.supportThreads(), api.myParties()];
      if (selectedThread?.id && !composeMode) requests.push(api.supportThread(selectedThread.id));
      const [threadResult, partyResult, threadDetail] = await Promise.all(requests);
      setThreads(readThreadItems(threadResult));
      setPartyOptions(readPartyOptions(partyResult));
      if (threadDetail) setSelectedThread(threadDetail);
    } catch (error) {
      if (!silent) setMessage(error.message || '문의 내역을 불러오지 못했습니다.');
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const openThread = async (thread) => {
    setComposeMode(false);
    setSelectedThread(thread);
    setLoading(true);
    setMessage('');
    try {
      const detail = await api.supportThread(thread.id);
      setSelectedThread(detail);
    } catch (error) {
      setMessage(error.message || '문의 상세를 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const startCompose = () => {
    setSelectedThread(null);
    setComposeMode(true);
    setDraft('');
    setMessage('');
  };

  const submitThread = async (event) => {
    event.preventDefault();
    if (!form.title.trim() || !form.content.trim()) {
      setMessage('제목과 내용을 입력해 주세요.');
      return;
    }

    setLoading(true);
    setMessage('');
    try {
      const detail = await api.createSupportThread({
        kind: form.kind,
        title: form.title.trim(),
        content: form.content.trim(),
        party_id: form.party_id ? Number(form.party_id) : null,
      });
      setSelectedThread(detail);
      setComposeMode(false);
      setForm(createInitialForm(routePreset));
      await loadSupportData({ silent: true });
    } catch (error) {
      setMessage(error.message || '문의를 접수하지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const submitMessage = async (event) => {
    event.preventDefault();
    if (!selectedThread || !draft.trim()) return;

    setLoading(true);
    setMessage('');
    try {
      const detail = await api.sendSupportMessage(selectedThread.id, { content: draft.trim() });
      setSelectedThread(detail);
      setDraft('');
      await loadSupportData({ silent: true });
    } catch (error) {
      setMessage(error.message || '메시지를 보내지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen-grid support-inbox-page">
      <section className="screen-hero-card compact">
        <button className="text-button back-button" type="button" onClick={() => navigate('/guide')}>
          <ArrowLeft size={17} />
          이용 안내로 돌아가기
        </button>
        <p className="eyebrow">Support</p>
        <h1>문의와 신고를 남겨주세요.</h1>
        <p>접수한 내용은 문의 번호로 관리되며 답변이 오면 같은 화면에서 이어서 확인할 수 있습니다.</p>
      </section>

      {message && <p className={message.includes('못했습니다') || message.includes('입력') ? 'error' : 'success'}>{message}</p>}

      <section className="support-desk workspace-card">
        <aside className="support-thread-list">
          <div className="support-list-head">
            <div>
              <p className="eyebrow">Threads</p>
              <h2>문의 내역</h2>
            </div>
            <button className="icon-button" type="button" onClick={startCompose} aria-label="새 문의 작성">
              <Plus size={18} />
            </button>
          </div>
          <div className="support-list-scroll">
            {threads.map((thread) => (
              <button
                className={selectedThread?.id === thread.id ? 'support-thread-item active' : 'support-thread-item'}
                key={thread.id}
                type="button"
                onClick={() => openThread(thread)}
              >
                <span>{thread.code || `Q${String(thread.id).padStart(5, '0')}`}</span>
                <strong>{thread.title}</strong>
                <small>{formatSupportKind(thread.kind)} · {formatSupportStatus(thread.status)}</small>
              </button>
            ))}
            {!threads.length && (
              <EmptyState
                icon={MessageCircle}
                title={loading ? '문의 내역을 불러오는 중입니다' : '문의 내역이 없습니다'}
                text="새 문의를 작성하면 이 영역에 표시됩니다."
              />
            )}
          </div>
        </aside>

        <div className="support-conversation">
          {composeMode ? (
            <form className="support-compose-form" onSubmit={submitThread}>
              <div className="card-title">
                <p className="eyebrow">{form.kind === 'report' ? 'Report' : 'Inquiry'}</p>
                <h2>{form.kind === 'report' ? '신고 내용을 작성해 주세요.' : '문의 내용을 작성해 주세요.'}</h2>
              </div>
              <label>
                <span>구분</span>
                <select value={form.kind} onChange={(event) => handleFormChange('kind', event.target.value)}>
                  <option value="inquiry">문의</option>
                  <option value="report">신고</option>
                </select>
              </label>
              <label>
                <span>제목</span>
                <input
                  placeholder="예: 파티 참여 후 채팅에 접근할 수 없어요."
                  value={form.title}
                  onChange={(event) => handleFormChange('title', event.target.value)}
                />
              </label>
              <label>
                <span>파티 선택</span>
                <select value={form.party_id} onChange={(event) => handleFormChange('party_id', event.target.value)}>
                  <option value="">선택하지 않음</option>
                  {partyOptions.map((party) => (
                    <option key={party.id} value={party.id}>
                      #{party.id} {party.start_place} → {party.end_place}
                    </option>
                  ))}
                </select>
              </label>
              {selectedParty && (
                <SupportPartyCard party={selectedParty} />
              )}
              <label>
                <span>내용</span>
                <textarea
                  placeholder="상황, 시간, 파티 정보, 확인한 화면 등을 구체적으로 적어 주세요."
                  value={form.content}
                  onChange={(event) => handleFormChange('content', event.target.value)}
                />
              </label>
              <button className="solid-button" type="submit" disabled={loading}>
                {form.kind === 'report' ? <ShieldAlert size={18} /> : <MessageCircle size={18} />}
                {form.kind === 'report' ? '신고하기' : '문의하기'}
              </button>
            </form>
          ) : (
            <SupportThreadDetail
              draft={draft}
              loading={loading}
              thread={selectedThread}
              onDraftChange={setDraft}
              onSubmit={submitMessage}
            />
          )}
        </div>
      </section>
    </div>
  );
}

function SupportThreadDetail({ draft, loading, onDraftChange, onSubmit, thread }) {
  if (!thread) {
    return (
      <div className="support-empty-panel">
        <MessageCircle size={28} />
        <p>문의 또는 신고를 선택해 주세요.</p>
      </div>
    );
  }

  return (
    <>
      <div className="support-chat-head">
        <div>
          <p className="eyebrow">{thread.code || `Q${String(thread.id).padStart(5, '0')}`}</p>
          <h2>{thread.title}</h2>
        </div>
        <span className={`support-status ${thread.status}`}>{formatSupportStatus(thread.status)}</span>
      </div>
      <article className="support-summary-card">
        <p>{thread.content}</p>
        {thread.party && <SupportPartyCard party={thread.party} />}
      </article>
      <div className="support-message-list" aria-live="polite">
        {getSupportTimelineItems(thread).map((item) => (
          item.type === 'event' ? (
            <SupportSystemNote key={item.key} text={item.content} />
          ) : (
            <article
              className={item.sender_role === 'user' ? 'support-message mine' : 'support-message'}
              key={item.key}
            >
              <span>{item.sender_name || (item.sender_role === 'user' ? '나' : '운영팀')}</span>
              <p>{item.content}</p>
              <time>{formatSupportDate(item.created_at)}</time>
            </article>
          )
        ))}
      </div>
      <form className="support-message-input" onSubmit={onSubmit}>
        <input
          placeholder="추가로 전달할 내용을 입력하세요"
          value={draft}
          onChange={(event) => onDraftChange(event.target.value)}
        />
        <button className="solid-button" type="submit" disabled={loading || !draft.trim()}>
          <Send size={17} />
          전송
        </button>
      </form>
    </>
  );
}

function SupportSystemNote({ text }) {
  return <div className="support-system-note">{text}</div>;
}

function SupportPartyCard({ party }) {
  return (
    <div className="support-party-card">
      <CheckCircle2 size={17} />
      <div>
        <strong>#{party.id} {party.start_place} → {party.end_place}</strong>
        <span>{formatSupportDate(party.departure_time)}</span>
      </div>
    </div>
  );
}

function readRoutePreset(route = '') {
  const query = route.split('?')[1] || '';
  const params = new URLSearchParams(query);
  return {
    kind: params.get('kind') === 'report' ? 'report' : 'inquiry',
    partyId: params.get('party_id') || '',
  };
}

function createInitialForm(preset) {
  return {
    kind: preset.kind,
    title: '',
    content: '',
    party_id: preset.partyId,
  };
}

function readThreadItems(result) {
  const items = result?.items || result?.threads || result || [];
  return Array.isArray(items) ? items : [];
}

function getVisibleSupportMessages(thread) {
  const messages = thread.messages || [];
  return messages.filter((message, index) => {
    if (index !== 0) return true;
    return !(message.sender_role === 'user' && message.content === thread.content);
  });
}

function getSupportTimelineItems(thread) {
  const events = (thread.events?.length ? thread.events : createFallbackSupportEvents(thread)).map((event) => ({
    ...event,
    type: 'event',
    key: `event-${event.id || event.event_type || event.created_at}`,
  }));
  const messages = getVisibleSupportMessages(thread).map((message) => ({
    ...message,
    type: 'message',
    key: `message-${message.id}`,
  }));

  return [...events, ...messages].sort((left, right) => new Date(left.created_at || 0) - new Date(right.created_at || 0));
}

function createFallbackSupportEvents(thread) {
  return [
    {
      id: 'created',
      event_type: 'created',
      content: '문의가 시작되었습니다. 개발자의 답변이 오기 전까지 다소 시간이 소요될 수 있습니다.',
      created_at: thread.created_at,
    },
    {
      id: 'status',
      event_type: 'status',
      content: `현재 상태가 ${formatSupportStatus(thread.status)}로 변경되었습니다.`,
      created_at: thread.updated_at || thread.created_at,
    },
  ];
}

function readPartyOptions(result) {
  const merged = [...(result?.created_parties || []), ...(result?.joined_parties || [])];
  const byId = new Map();
  merged.forEach((party) => {
    if (party?.id) byId.set(party.id, party);
  });
  return [...byId.values()];
}

function formatSupportKind(value) {
  return value === 'report' ? '신고' : '문의';
}

function formatSupportStatus(value) {
  const labels = {
    open: '접수',
    in_progress: '진행 중',
    resolved: '완료',
  };
  return labels[value] || value || '접수';
}

function formatSupportDate(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('ko-KR', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}
