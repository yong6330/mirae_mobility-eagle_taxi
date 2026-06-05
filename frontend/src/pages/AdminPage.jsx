import { BarChart3, MessageSquareText, Users } from 'lucide-react';
import EmptyState from '../components/EmptyState';

export default function AdminPage({ user }) {
  if (user?.role !== 'admin') {
    return (
      <div className="screen-grid">
        <section className="screen-hero-card compact">
          <p className="eyebrow">Admin</p>
          <h1>관리자 권한이 필요합니다</h1>
          <p>관리자 화면은 admin 권한을 가진 사용자만 접근할 수 있습니다.</p>
        </section>
      </div>
    );
  }

  return (
    <div className="screen-grid">
      <section className="screen-hero-card compact">
        <p className="eyebrow">Admin</p>
        <h1>관리자 페이지</h1>
        <p>서비스 통계, 사용자 데이터, 파티 데이터, 최근 메시지를 확인하는 화면입니다.</p>
      </section>

      <section className="admin-metrics">
        <article><Users size={22} /><span>사용자 수</span><strong>API 연결 전</strong></article>
        <article><BarChart3 size={22} /><span>전체 파티 수</span><strong>API 연결 전</strong></article>
        <article><MessageSquareText size={22} /><span>메시지 수</span><strong>API 연결 전</strong></article>
      </section>

      <section className="workspace-card">
        <h2>최근 파티와 사용자</h2>
        <EmptyState
          title="관리자 데이터가 없습니다"
          text="관리자 통계와 사용자 관리 정보가 이 영역에 표시됩니다."
        />
      </section>
    </div>
  );
}
