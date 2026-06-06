import BrandName from '../components/BrandName';
import EagleMark from '../components/EagleMark';
import SystemFooter from '../components/SystemFooter';

export const TERMS_SECTIONS = [
  ['서비스 목적', 'Eagle Taxi는 연세대학교 미래캠퍼스 학생들이 같은 이동 조건의 택시 파티를 찾고 만들 수 있도록 돕는 학생 간 이동 파티 중개 서비스입니다.'],
  ['계정과 이용 자격', '이용자는 정확한 학교 이메일과 기본 정보를 입력해야 하며, 타인의 계정을 사용하거나 허위 정보를 입력해서는 안 됩니다.'],
  ['파티 생성과 참여', '이용자는 출발지, 목적지, 출발 시간, 만남 장소를 가능한 한 정확하게 입력해야 하며, 참여 후에는 파티원과 필요한 안내를 성실히 조율해야 합니다.'],
  ['요금과 결제', '서비스에 표시되는 요금은 예상 금액이며 실제 요금과 다를 수 있습니다. 실제 결제, 정산, 영수증 처리는 파티원 간 별도로 진행합니다.'],
  ['안전과 책임', '이용자는 탑승 전 파티 정보와 동승자를 확인해야 합니다. 위험하거나 부적절한 상황이 발생하면 즉시 이용을 중단하고 도움을 요청해야 합니다.'],
  ['제공하지 않는 기능', 'Eagle Taxi는 실제 택시 호출, 배차, 운전자 연결, 결제, 실시간 위치 추적을 제공하지 않습니다.'],
  ['서비스 변경', '운영 상황에 따라 기능, 화면, 정책은 변경될 수 있으며 중요한 변경 사항은 서비스 화면 또는 공지로 안내합니다.'],
];

export const PRIVACY_SECTIONS = [
  ['수집하는 정보', '이메일, 비밀번호 해시, 이름 또는 닉네임, 성별, 파티 생성·참여 정보, 채팅 메시지, 문의 및 신고 내용을 서비스 운영에 필요한 범위에서 처리합니다.'],
  ['이용 목적', '회원 식별, 파티 추천과 검색, 파티 참여 관리, 채팅 제공, 문의 대응, 신고 확인, 서비스 품질 개선을 위해 정보를 사용합니다.'],
  ['보관 기간', '서비스 운영에 필요한 기간 동안 정보를 보관하며, 계정 삭제 또는 운영 종료 시 관련 법령과 내부 보관 기준에 따라 정리합니다.'],
  ['제3자 제공', '이용자의 개인정보를 외부에 판매하거나 임의 제공하지 않습니다. 다만 법령상 요청이 있거나 이용자의 안전 확보가 필요한 경우 필요한 범위에서 처리할 수 있습니다.'],
  ['수집하지 않는 정보', '결제 카드 정보, 실제 위치 추적 정보, 운전자 정보, 실제 택시 호출 정보는 수집하지 않습니다.'],
  ['이용자의 권리', '이용자는 본인의 개인정보 열람, 정정, 삭제 요청을 할 수 있으며 서비스 운영자는 가능한 범위에서 신속하게 처리합니다.'],
  ['보호 조치', '비밀번호는 해시 처리하고, 접근 권한을 최소화하며, 서비스 운영 목적 외 사용을 제한합니다.'],
];

export default function LegalPage({ type, navigate }) {
  const isPrivacy = type === 'privacy';
  const sections = isPrivacy ? PRIVACY_SECTIONS : TERMS_SECTIONS;

  return (
    <main className="landing-page legal-shell">
      <header className="site-header simple">
        <button className="brand-button" type="button" onClick={() => navigate('/')}>
          <EagleMark small />
          <BrandName />
        </button>
        <div className="header-actions">
          <button className="quiet-button" type="button" onClick={() => navigate('/guide')}>이용 안내</button>
          <button className="solid-button" type="button" onClick={() => navigate('/main')}>서비스 메인</button>
        </div>
      </header>

      <section className="legal-page expanded">
        <p className="eyebrow">{isPrivacy ? '개인정보 처리방침' : '이용약관'}</p>
        <h1>{isPrivacy ? '개인정보 처리방침' : '이용약관'}</h1>
        <p className="legal-lead">
          {isPrivacy
            ? 'Eagle Taxi는 서비스 운영에 필요한 최소한의 정보를 처리하고, 이용자의 정보를 안전하게 관리하기 위해 노력합니다.'
            : 'Eagle Taxi를 이용하기 전 아래 약관을 확인해 주세요. 서비스는 학생 간 이동 파티를 돕는 정보 중개를 중심으로 운영됩니다.'}
        </p>
        <div className="legal-card expanded">
          {sections.map(([title, text]) => (
            <article key={title}>
              <h2>{title}</h2>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>
      <SystemFooter navigate={navigate} />
    </main>
  );
}
