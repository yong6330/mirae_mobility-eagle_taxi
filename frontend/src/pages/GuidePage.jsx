import { LifeBuoy, MessageCircle } from 'lucide-react';
import HowToUseSection from '../components/HowToUseSection';

const FAQ_ITEMS = [
  ['파티 추천이 없으면 어떻게 하나요?', '같은 조건으로 바로 새 파티를 만들거나, 파티 목록에서 조건을 넓혀 다시 확인할 수 있습니다.'],
  ['출발 시간이 바뀌면 어떻게 하나요?', '파티 상세와 채팅에서 참여자에게 변경 내용을 알려 만남 시간을 다시 조율해 주세요.'],
  ['문제가 생기면 어디에 남기나요?', '파티 상세 화면의 신고하기 버튼을 눌러 상황을 남겨 주세요.'],
];

export default function GuidePage({ navigate }) {
  return (
    <div className="screen-grid support-page">
      <section className="screen-hero-card compact support-hero">
        <div>
          <p className="eyebrow">Guide</p>
          <h1>이용 안내</h1>
          <p>이용 방법과 자주 묻는 질문을 확인할 수 있습니다.</p>
        </div>
        <button className="solid-button" type="button" onClick={() => navigate('/support?kind=inquiry')}>
          <MessageCircle size={18} />
          1:1 문의하기
        </button>
      </section>

      <HowToUseSection className="guide-method-section" />

      <section className="workspace-card support-form-card">
        <div className="card-title">
          <p className="eyebrow">자주 묻는 질문</p>
          <h2>빠르게 확인하세요.</h2>
        </div>
        <div className="faq-list">
          {FAQ_ITEMS.map(([title, text]) => (
            <article key={title}>
              <LifeBuoy size={18} />
              <div>
                <strong>{title}</strong>
                <p>{text}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
