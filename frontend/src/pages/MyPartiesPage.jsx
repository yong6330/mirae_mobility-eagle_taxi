import { useEffect, useMemo, useState } from 'react';
import { Ban, ClipboardList, Plus } from 'lucide-react';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState';
import PartyCard from '../components/PartyCard';

export default function MyPartiesPage({ navigate }) {
  const [createdParties, setCreatedParties] = useState([]);
  const [joinedParties, setJoinedParties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const allParties = useMemo(() => mergeMyParties(createdParties, joinedParties), [createdParties, joinedParties]);
  const activeParties = useMemo(
    () => allParties.filter((party) => ['recruiting', 'matched'].includes(party.status)),
    [allParties],
  );
  const historyParties = useMemo(
    () => allParties.filter((party) => !['recruiting', 'matched'].includes(party.status)),
    [allParties],
  );

  useEffect(() => {
    loadMyParties();
  }, []);

  const loadMyParties = async () => {
    setLoading(true);
    setMessage('');
    try {
      const result = await api.myParties();
      setCreatedParties(result.created_parties || []);
      setJoinedParties(result.joined_parties || []);
    } catch (error) {
      setMessage(error.message || '내 이동 목록을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelParty = async (party) => {
    if (!window.confirm('생성한 파티를 취소할까요?')) return;
    setLoading(true);
    setMessage('');

    try {
      await api.cancelParty(party.id, { cancel_reason: '생성자 취소' });
      await loadMyParties();
      setMessage('파티가 취소되었습니다.');
    } catch (error) {
      setMessage(error.message || '파티 취소에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen-grid">
      <section className="screen-hero-card compact">
        <p className="eyebrow">My Trips / 내 이동</p>
        <h1>내 이동</h1>
        <p>참여 중인 이동과 지난 이동을 확인합니다.</p>
      </section>

      {message && <p className="error">{message}</p>}

      <section className="split-panels my-trips-sections">
        <article className="workspace-card">
          <div className="card-title row">
            <div>
              <p className="eyebrow">Active</p>
              <h2>활성화 중인 파티</h2>
            </div>
            <button className="solid-button" type="button" onClick={() => navigate('/parties/new')}>
              <Plus size={18} />
              이동 파티 만들기
            </button>
          </div>

          {activeParties.length > 0 ? (
            <div className="party-list single">
              {activeParties.map((party) => (
                <PartyCard
                  key={party.id}
                  navigate={navigate}
                  party={party}
                  actions={party.relation === 'created' ? (
                    <button
                      className="quiet-button danger"
                      type="button"
                      onClick={() => handleCancelParty(party)}
                      disabled={loading || !canCancelParty(party)}
                    >
                      <Ban size={17} />
                      파티 취소
                    </button>
                  ) : null}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={ClipboardList}
              title={loading ? '활성화 중인 파티를 불러오는 중입니다' : '활성화 중인 파티가 없습니다'}
              text="참여 중인 이동 파티가 있으면 이 영역에 표시됩니다."
              action={<button className="solid-button" type="button" onClick={() => navigate('/parties/new')}><Plus size={18} /> 이동 파티 만들기</button>}
            />
          )}
        </article>

        <article className="workspace-card">
          <div className="card-title">
            <p className="eyebrow">History</p>
            <h2>지난 이동 내역</h2>
          </div>

          {historyParties.length > 0 ? (
            <div className="party-list single">
              {historyParties.map((party) => (
                <PartyCard key={party.id} navigate={navigate} party={party} />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={ClipboardList}
              title={loading ? '지난 이동 내역을 불러오는 중입니다' : '지난 이동 내역이 없습니다'}
              text="완료, 취소, 만료된 파티가 있으면 이 영역에 표시됩니다."
            />
          )}
        </article>
      </section>
    </div>
  );
}

function canCancelParty(party) {
  return ['recruiting', 'matched'].includes(party?.status);
}

function mergeMyParties(createdParties, joinedParties) {
  const byId = new Map();
  createdParties.forEach((party) => {
    if (party?.id) byId.set(party.id, { ...party, relation: 'created' });
  });
  joinedParties.forEach((party) => {
    if (party?.id && !byId.has(party.id)) byId.set(party.id, { ...party, relation: 'joined' });
  });
  return [...byId.values()].sort((left, right) => new Date(right.departure_time || right.created_at || 0) - new Date(left.departure_time || left.created_at || 0));
}
