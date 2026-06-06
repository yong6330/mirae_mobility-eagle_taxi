import { useState } from 'react';
import { CheckCircle2, Clock3, MapPinned, MessageCircle, MousePointer2, Search } from 'lucide-react';
import BrandName from './BrandName';
import EagleMark from './EagleMark';

const METHOD_STEPS = [
  {
    icon: MapPinned,
    number: '01',
    title: '위치 선택',
    text: '출발지와 목적지를 검색하고 지도에서 경로를 확인합니다.',
  },
  {
    icon: Clock3,
    number: '02',
    title: '시간 설정',
    text: '현재 시간을 기준으로 빠르게 선택하거나 원하는 시간을 직접 조정합니다.',
  },
  {
    icon: Search,
    number: '03',
    title: '파티 비교',
    text: '비슷한 조건의 파티가 있으면 먼저 추천 결과를 확인합니다.',
  },
  {
    icon: MessageCircle,
    number: '04',
    title: '만남 조율',
    text: '참여 후 상세 화면과 채팅에서 만남 장소와 안내를 정리합니다.',
  },
];

export default function HowToUseSection({ className = '' }) {
  const [activeStep, setActiveStep] = useState(null);

  return (
    <section className={`landing-section method-section ${className}`.trim()} id="method">
      <div className="section-heading compact">
        <p className="section-kicker"><span>How to use</span></p>
        <h2>이용 방법</h2>
      </div>

      <div className="method-layout">
        <div className="method-step-list">
          {METHOD_STEPS.map((step, index) => {
            const Icon = step.icon;
            return (
              <button
                className={activeStep === index ? 'method-step-card is-active' : 'method-step-card'}
                key={step.title}
                type="button"
                onFocus={() => setActiveStep(index)}
                onMouseEnter={() => setActiveStep(index)}
              >
                <span>{step.number}</span>
                <Icon size={19} />
                <strong>{step.title}</strong>
                <p>{step.text}</p>
              </button>
            );
          })}
        </div>

        <div className="method-demo-panel" aria-live="polite">
          {activeStep === null ? <MethodIdle /> : <MethodPreview step={activeStep} />}
        </div>
      </div>
    </section>
  );
}

function MethodIdle() {
  return (
    <div className="method-idle">
      <EagleMark />
      <BrandName />
    </div>
  );
}

function MethodPreview({ step }) {
  if (step === 0) {
    return (
      <div className="demo-phone demo-location">
        <DemoTopbar title="위치 선택" />
        <div className="demo-field-stack">
          <DemoField label="출발지" value="학생회관" />
          <DemoField label="목적지" value="원주역" delay />
        </div>
        <div className="demo-mini-map">
          <svg className="demo-route-svg" viewBox="0 0 100 100" aria-hidden="true">
            <path d="M24 72 C44 72 45 25 76 25" />
          </svg>
          <i className="demo-pin start" />
          <i className="demo-pin end" />
          <small className="demo-map-label start">학생회관</small>
          <small className="demo-map-label end">원주역</small>
        </div>
      </div>
    );
  }

  if (step === 1) {
    return (
      <div className="demo-phone demo-time">
        <DemoTopbar title="시간 설정" />
        <div className="demo-time-picker" aria-hidden="true">
          <div className="demo-time-column hour">
            <span>20</span>
            <span>19</span>
            <strong>18</strong>
            <span>17</span>
            <span>16</span>
          </div>
          <em>:</em>
          <div className="demo-time-column minute">
            <span>00</span>
            <span>15</span>
            <strong>30</strong>
            <span>45</span>
            <span>00</span>
          </div>
        </div>
        <button className="demo-check-button" type="button">
          빠른 시작
        </button>
        <button className="demo-list-button" type="button">
          파티 목록
        </button>
      </div>
    );
  }

  if (step === 2) {
    return (
      <div className="demo-phone demo-match">
        <DemoTopbar title="파티 비교" />
        <div className="demo-match-backdrop">
          <article className="demo-party-popup">
            <span>추천 파티</span>
            <strong>학생회관 → 원주역</strong>
            <div className="demo-party-meta">
              <small>출발 18:30</small>
              <small>현재 2/4명</small>
            </div>
            <div className="demo-party-actions">
              <button type="button">파티 참여</button>
              <button type="button">파티 목록</button>
            </div>
          </article>
          <MousePointer2 className="demo-cursor match-cursor" size={24} />
          <div className="demo-confirm-layer">
            <CheckCircle2 size={42} />
            <strong>참여 완료</strong>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="demo-phone demo-chat">
      <DemoTopbar title="만남 조율" />
      <div className="demo-chat-summary">
        <span><strong>출발</strong><em>학생회관</em></span>
        <span><strong>도착</strong><em>원주역</em></span>
        <span><strong>요금</strong><em>4,200원</em></span>
        <span><strong>인원</strong><em>3/4명</em></span>
      </div>
      <div className="demo-chat-thread">
        <p className="mine first">우리 지금 만나</p>
        <p className="mine second">당장 만나</p>
        <p className="third">엉 당장 만나</p>
      </div>
    </div>
  );
}

function DemoTopbar({ title }) {
  return (
    <div className="demo-topbar">
      <span />
      <strong>{title}</strong>
      <span />
    </div>
  );
}

function DemoField({ delay = false, label, value }) {
  return (
    <label className={delay ? 'demo-input-field delay' : 'demo-input-field'}>
      <span>{label}</span>
      <strong><i>{value}</i></strong>
      <CheckCircle2 size={18} />
    </label>
  );
}
