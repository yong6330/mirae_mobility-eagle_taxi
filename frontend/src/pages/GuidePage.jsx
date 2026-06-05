import { ShieldCheck } from 'lucide-react';

const GUIDE_ITEMS = [
  ['서비스 한계', '독수리 택시는 실제 택시 호출, 배차, 결제, 운전자 연결을 제공하지 않습니다.'],
  ['요금 안내', '예상 택시비와 실제 요금은 다를 수 있습니다. 실제 결제는 파티원 간 별도 조율이 필요합니다.'],
  ['안전 안내', '탑승 전 파티 정보와 만남 장소를 확인하고, 필요하면 채팅으로 세부 사항을 조율하세요.'],
  ['신고 안내', '신고 버튼은 MVP에서 안내용으로 제공되며 저장 API는 호출하지 않습니다.'],
];

export default function GuidePage({ navigate }) {
  return (
    <div className="screen-grid">
      <section className="screen-hero-card compact">
        <p className="eyebrow">Guide</p>
        <h1>안전 안내</h1>
        <p>서비스 이용 전 요금, 안전, 개인정보, MVP 범위를 확인하는 화면입니다.</p>
      </section>

      <section className="feature-grid guide-grid">
        {GUIDE_ITEMS.map(([title, text]) => (
          <article className="workspace-card guide-card" key={title}>
            <ShieldCheck size={22} />
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </section>

      <section className="workspace-card action-row">
        <button className="solid-button" type="button" onClick={() => navigate('/main')}>메인으로 이동</button>
        <button className="quiet-button" type="button" onClick={() => navigate('/terms')}>이용약관 보기</button>
        <button className="quiet-button" type="button" onClick={() => navigate('/privacy')}>개인정보 처리방침 보기</button>
      </section>
    </div>
  );
}
