export default function LegalPage({ type, navigate }) {
  const isPrivacy = type === 'privacy';

  return (
    <main className="landing-page">
      <header className="site-header simple">
        <button className="brand-button" type="button" onClick={() => navigate('/')}>독수리 택시</button>
        <div className="header-actions">
          <button className="quiet-button" type="button" onClick={() => navigate('/guide')}>안전 안내</button>
          <button className="solid-button" type="button" onClick={() => navigate('/main')}>메인으로 이동</button>
        </div>
      </header>

      <section className="legal-page">
        <p className="eyebrow">{isPrivacy ? 'Privacy' : 'Terms'}</p>
        <h1>{isPrivacy ? '개인정보 처리방침 안내' : '이용약관 안내'}</h1>
        <div className="legal-card">
          {isPrivacy ? (
            <>
              <h2>수집 정보</h2>
              <p>이메일, 비밀번호 해시, 이름 또는 닉네임, 성별, 파티 생성·참여 정보, 채팅 메시지를 MVP 개발·시연 범위에서 사용합니다.</p>
              <h2>제외 정보</h2>
              <p>결제 정보, 실제 위치 추적 정보, 운전자 정보, 실제 택시 호출 정보는 수집하지 않습니다.</p>
            </>
          ) : (
            <>
              <h2>서비스 목적</h2>
              <p>독수리 택시는 학생 간 택시 합승 파티 생성과 검색을 돕는 중개 플랫폼입니다.</p>
              <h2>서비스 한계</h2>
              <p>실제 택시 호출, 배차, 결제, 운전자 연결은 이번 MVP 범위에 포함하지 않습니다.</p>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
