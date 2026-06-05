import { useEffect, useState } from 'react';
import { Ban, ClipboardList, Plus } from 'lucide-react';
import { api } from '../api/client';
import EmptyState from '../components/EmptyState';
import PartyCard from '../components/PartyCard';

export default function MyPartiesPage({ navigate }) {
  const [createdParties, setCreatedParties] = useState([]);
  const [joinedParties, setJoinedParties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

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
      setMessage(error.message || '내 파티 목록을 불러오지 못했습니다.');
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
        <p className="eyebrow">My Parties</p>
        <h1>내 파티</h1>
        <p>내가 만든 파티와 참여 중인 파티를 구분해서 확인합니다.</p>
      </section>

      {message && <p className="error">{message}</p>}

      <section className="split-panels">
        <article className="workspace-card">
          <div className="card-title row">
            <div>
              <p className="eyebrow">Created</p>
              <h2>내가 만든 파티</h2>
            </div>
            <button className="solid-button" type="button" onClick={() => navigate('/parties/new')}>
              <Plus size={18} />
              파티 만들기
            </button>
          </div>

          {createdParties.length > 0 ? (
            <div className="party-list single">
              {createdParties.map((party) => (
                <PartyCard
                  key={party.id}
                  navigate={navigate}
                  party={party}
                  actions={(
                    <button
                      className="quiet-button danger"
                      type="button"
                      onClick={() => handleCancelParty(party)}
                      disabled={loading || !canCancelParty(party)}
                    >
                      <Ban size={17} />
                      파티 취소
                    </button>
                  )}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={ClipboardList}
              title={loading ? '내가 만든 파티를 불러오는 중입니다' : '생성한 파티가 없습니다'}
              text="파티를 생성하면 이 영역에 표시됩니다."
              action={<button className="solid-button" type="button" onClick={() => navigate('/parties/new')}><Plus size={18} /> 파티 만들기</button>}
            />
          )}
        </article>

        <article className="workspace-card">
          <div className="card-title">
            <p className="eyebrow">Joined</p>
            <h2>참여 중인 파티</h2>
          </div>

          {joinedParties.length > 0 ? (
            <div className="party-list single">
              {joinedParties.map((party) => (
                <PartyCard key={party.id} navigate={navigate} party={party} />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={ClipboardList}
              title={loading ? '참여 중인 파티를 불러오는 중입니다' : '참여 중인 파티가 없습니다'}
              text="조건에 맞는 파티에 참여하면 이 영역에 표시됩니다."
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
