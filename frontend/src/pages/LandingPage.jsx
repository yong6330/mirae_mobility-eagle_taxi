import {
  ArrowRight,
  Clock3,
  LogIn,
  Moon,
  ShieldCheck,
  Sparkles,
  Sun,
  Users,
  WalletCards,
} from 'lucide-react';
import BrandName from '../components/BrandName';
import BusChart from '../components/BusChart';
import EagleMark from '../components/EagleMark';
import HowToUseSection from '../components/HowToUseSection';
import SystemFooter from '../components/SystemFooter';
import { VERSION } from '../constants/team';

const REVIEWS = [
  {
    score: '3/5점',
    stars: 3,
    text: '학교에서 원주역은 6천원, 고토까지는 7천원? 야간일때는 할증 붙어서 8천원? 왜 요금이 일정하지 않냐?',
    date: '2026.5.3.',
  },
  {
    score: '1/5점',
    stars: 1,
    text: '오늘 연택 불러서 타고 갔는데 자꾸 돌아가다가 고속 버스 놓쳤음..',
    date: '2026.1.28.',
  },
  {
    score: '2/5점',
    stars: 2,
    text: '호출 택시가 도착했는데 다른 합승 손님을 먼저 데려간다고 해서 신고하겠다고 했습니다.',
    date: '2026.5.1.',
  },
];

const INTRO_FEATURES = [
  {
    icon: WalletCards,
    title: '명확한 요금 산정 기준',
    text: '임의 요금이 아닌 택시 미터기 기반 요금, 예상 택시비를 기준으로 참여 인원별 1인 부담금 계산',
  },
  {
    icon: ShieldCheck,
    title: '확인 가능한 안전 장치',
    text: '학교 구성원 중심의 이용자 정보 확인으로 본인 확인, 신고 기능, 동성 매칭 등 안전 장치 확보',
  },
  {
    icon: Users,
    title: '손쉬운 파티 관리',
    text: '파티 생성부터 참여, 매칭 완료, 취소까지 전체 과정을 관리, 모집 상태를 명확히 표시해 진행 상황 한눈에 파악',
  },
  {
    icon: Clock3,
    title: '투명한 이동 정보 공유',
    text: '출발지, 도착지, 희망 시간, 현재 인원 등 핵심 정보를 파악하고 조건에 맞는 파티 검색, 추천 받아 참여 가능',
  },
];

const TEAM = [
  ['PM / 프로젝트 총괄', '용석희'],
  ['OM / 운영 총괄', '최우진'],
  ['TL & Backend / 백엔드 및 종합', '이가람'],
  ['QA&Frontend / 품질 및 프론트엔드', '심지수'],
];

export default function LandingPage({ isAuthenticated, navigate, theme, onToggleTheme }) {
  const isDark = theme === 'dark';
  const startRoute = isAuthenticated ? '/main' : '/login';

  return (
    <main className="landing-page studio-landing">
      <header className="site-header studio-header">
        <button className="brand-button" type="button" onClick={() => navigate('/')}>
          <EagleMark small />
          <BrandName />
          <em>v{VERSION}</em>
        </button>

        <nav className="site-nav" aria-label="랜딩 화면 섹션">
          <a href="#background-one">서비스 배경</a>
          <a href="#introduce">서비스 소개</a>
          <a href="#method">이용 방법</a>
          <a href="#team">개발자 정보</a>
        </nav>

        <div className="header-actions">
          <button className="icon-button" type="button" onClick={onToggleTheme} aria-label="테마 전환">
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <button className="quiet-button" type="button" onClick={() => navigate(isAuthenticated ? '/main' : '/login')}>
            <LogIn size={17} />
            {isAuthenticated ? '서비스 메인' : '로그인'}
          </button>
          <button className="solid-button" type="button" onClick={() => navigate(startRoute)}>
            시작하기
          </button>
        </div>
      </header>

      <section className="landing-hero studio-hero centered-hero" aria-labelledby="landing-title">
        <div className="hero-copy">
          <EagleMark />
          <div className="hero-brand-line">
            <span>Mirae Mobility</span>
            <BrandName className="hero-brand-name" />
          </div>
          <h1 id="landing-title">우리의 이동이 시작됩니다.</h1>
          <p className="hero-line">출발지와 목적지를 입력하고 파티를 만들어보세요!</p>
          <div className="hero-buttons">
            <button className="solid-button large magnetic-button" type="button" onClick={() => navigate(startRoute)}>
              시작하기
              <ArrowRight size={19} />
            </button>
            <a className="quiet-button large magnetic-button" href="#method">
              이용 방법
            </a>
          </div>
        </div>
      </section>

      <section className="landing-section background-section" id="background-one">
        <div className="section-heading">
          <p className="section-kicker"><span>서비스 배경 I</span></p>
          <h2>교통 인프라의 <span className="accent-word">한계</span></h2>
          <p>
            우리 학교는 시내와 떨어져 있어 <strong>교통 선택지가 제한적</strong>입니다.
            교통 인프라가 불편해 학생들은 택시를 다수 이용하는데
            <strong> 택시비 부담</strong>을 줄이기 위해 학생들 사이에서는
            <strong> 불법 합승 택시 이용 관행</strong>이 존재합니다.
          </p>
        </div>
        <BusChart />
      </section>

      <section className="landing-section background-section" id="background-two">
        <div className="section-heading">
          <p className="section-kicker"><span>서비스 배경 II</span></p>
          <h2><span className="accent-word">불법 택시</span> 이용해 보셨나요?</h2>
          <p>
            20년째 명맥을 이어오는 불법 합승 택시, 연택은 저렴하고 편리하다는 장점 때문에 학생 수요가 있으나
            운전자가 임의로 학생을 합승시키고 미터기 없이 요금을 임의로 받는 구조라 불법이며 요금 투명성,
            안전성, 이용자 정보 확인 측면에서 한계가 있습니다.
          </p>
        </div>
        <div className="review-grid">
          {REVIEWS.map((review, index) => (
            <article className="review-card interactive-card" key={review.date}>
              <span>리뷰 {index + 1}</span>
              <strong>{review.score}</strong>
              <div className="star-row" aria-label={`${review.stars}점`}>
                {'★★★★★'.split('').map((star, starIndex) => (
                  <b className={starIndex < review.stars ? 'filled' : ''} key={`${review.date}-${starIndex}`}>{star}</b>
                ))}
              </div>
              <p>{review.text}</p>
              <time>{review.date}</time>
            </article>
          ))}
        </div>
        <p className="source-note">실제 최근 학생 커뮤니티 사용자 의견 *평점은 임의로 구성했습니다.</p>
      </section>

      <section className="landing-section feature-section" id="introduce">
        <div className="section-heading compact">
          <p className="section-kicker"><span>서비스 소개</span></p>
          <h2>저렴하고 안전한 <BrandName /></h2>
          <p>직접 파티를 생성하고 참여할 수 있는 택시 합승 중개 플랫폼</p>
        </div>
        <div className="landing-feature-grid">
          {INTRO_FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <article className="feature-tile interactive-card" key={feature.title}>
                <Icon size={24} />
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </article>
            );
          })}
        </div>
      </section>

      <HowToUseSection />

      <section className="landing-section developer-section" id="team">
        <div className="section-heading compact">
          <p className="section-kicker"><span>Mirae Mobility</span></p>
          <h2>개발자 정보</h2>
          <p>
            연세대학교 미래캠퍼스 컴퓨팅사고 강의 프로젝트로 시작된
            <span className="inline-brand"> Eagle Taxi</span>는 학생들의 캠퍼스 이동을 안전하고 더 가볍게 만들기 위해 개발되었습니다.
          </p>
        </div>
        <div className="developer-grid">
          {TEAM.map(([role, text]) => (
            <article className="developer-card interactive-card" key={role}>
              <span>{role}</span>
              <strong>{text}</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-cta kinetic-cta">
        <div className="cta-motion" aria-hidden="true">
          <i />
          <i />
          <i />
          <span />
          <span />
          <span />
          <b />
          <b />
        </div>
        <p className="section-kicker"><span>START EAGLE TAXI</span></p>
        <h2>자, 이제 출발해볼까요?</h2>
        <p>출발지와 목적지를 입력하고 같은 방향의 학생을 찾아보세요.</p>
        <div className="hero-buttons">
          <button className="solid-button large magnetic-button" type="button" onClick={() => navigate(startRoute)}>
            시작하기
            <Sparkles size={19} />
          </button>
        </div>
      </section>

      <SystemFooter navigate={navigate} />
    </main>
  );
}
