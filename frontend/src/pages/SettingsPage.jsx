import { useState } from 'react';
import { CreditCard, LogOut } from 'lucide-react';
import InfoRow from '../components/InfoRow';

export default function SettingsPage({ onLogout, user }) {
  const [notice, setNotice] = useState('');
  const rows = [
    ['이름', user?.name || '정보 없음'],
    ['이메일', user?.email || '정보 없음'],
    ['성별', formatGender(user?.gender)],
    ['계정 생성일', formatDateTime(user?.created_at)],
  ];

  return (
    <div className="screen-grid">
      <section className="screen-hero-card compact">
        <p className="eyebrow">Settings</p>
        <h1>계정·설정</h1>
        <p>계정 정보와 서비스 설정 메뉴를 확인합니다.</p>
      </section>

      <section className="workspace-card">
        <h2>계정 정보</h2>
        <div className="profile-list">
          {rows.map(([label, value]) => (
            <InfoRow key={label} label={label} value={value} />
          ))}
        </div>
      </section>

      {notice && <p className="notice-message">{notice}</p>}

      <section className="workspace-card action-row">
        <button
          className="quiet-button"
          type="button"
          onClick={() => setNotice('결제수단 등록은 현재 서비스 범위에서 안내만 제공됩니다.')}
        >
          <CreditCard size={18} />
          결제수단
        </button>
        <button className="solid-button" type="button" onClick={onLogout}><LogOut size={18} /> 로그아웃</button>
      </section>
    </div>
  );
}

function formatGender(gender) {
  if (gender === 'male') return '남성';
  if (gender === 'female') return '여성';
  return '정보 없음';
}

function formatDateTime(value) {
  if (!value) return '정보 없음';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}
