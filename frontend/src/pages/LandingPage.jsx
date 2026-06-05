import {
  ArrowRight,
  LogIn,
  Moon,
  Plus,
  Search,
  Sparkles,
  Sun,
  WalletCards,
} from 'lucide-react';
import BusChart from '../components/BusChart';
import EagleMark from '../components/EagleMark';
import FeatureCard from '../components/FeatureCard';
import StepCard from '../components/StepCard';
import { TEAM_ROLES, VERSION } from '../constants/team';

const FEATURES = [
  {
    icon: Plus,
    title: '파티 생성',
    text: '출발지, 목적지, 출발 시간을 입력해 새 택시 파티를 만듭니다.',
  },
  {
    icon: Search,
    title: '파티 검색',
    text: '출발지, 목적지, 출발 시간 조건을 입력해 모집 중인 파티를 조회합니다.',
  },
  {
    icon: Sparkles,
    title: '유사 파티 추천',
    text: '입력한 이동 조건과 비슷한 파티를 추천받아 빠르게 비교합니다.',
  },
  {
    icon: WalletCards,
    title: '예상 택시비 분담 (MVP 수준에서는 구현 안 함)',
    text: '예상 요금과 1인 부담 금액을 안내합니다. 실제 분할 결제는 MVP 수준에서는 구현하지 않습니다.',
  },
];

const SOLUTION_FLOW = [
  ['조건 기반 검색', '출발지, 도착지, 출발 시간을 기준으로 택시 파티를 찾습니다.'],
  ['파티 생성', '조건에 맞는 파티가 없으면 직접 새 파티를 만들 수 있습니다.'],
  ['유사 조건 추천', '비슷한 이동 조건을 가진 모집 중 파티를 추천받습니다.'],
  ['비용 분담', '함께 택시를 이용하고 부담되는 이동 비용을 여러 명이 나눕니다.'],
];

const HERO_STEPS = [
  ['Step. 1', '사용자 정보 입력', '학교 이메일과 기본 정보를 입력해 계정을 준비합니다.'],
  ['Step. 2', '파티 생성 & 조회', '출발지, 목적지, 출발 시간 조건으로 파티를 찾습니다.'],
  ['Step. 3', '파티 참가', '조건이 맞는 파티에 참여하거나 새 파티를 생성합니다.'],
  ['Step. 4', '이용 & 정산', '택시를 함께 이용하고 부담 금액을 확인합니다. 실제 분할 결제는 MVP 수준에서는 구현하지 않습니다.'],
];

export default function LandingPage({ isAuthenticated, navigate, theme, onToggleTheme }) {
  const isDark = theme === 'dark';
  const startRoute = isAuthenticated ? '/main' : '/login';

  return (
    <main className="landing-page">
      <header className="site-header">
        <button className="brand-button" type="button" onClick={() => navigate('/')}>
          <EagleMark small />
          <span>독수리 택시</span>
          <em>Version {VERSION}</em>
        </button>

        <nav className="site-nav" aria-label="랜딩 화면 섹션">
          <a href="#problem">서비스 배경</a>
          <a href="#features">주요 기능</a>
          <a href="#usage">사용 방법</a>
        </nav>

        <div className="header-actions">
          <button className="icon-button" type="button" onClick={onToggleTheme} aria-label="테마 전환">
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <button className="quiet-button" type="button" onClick={() => navigate('/login')}>
            <LogIn size={17} />
            로그인
          </button>
          <button className="solid-button" type="button" onClick={() => navigate('/signup')}>
            회원가입
          </button>
        </div>
      </header>

      <section className="landing-hero" aria-labelledby="landing-title">
        <div className="hero-copy">
          <p className="eyebrow">Yonsei Mirae Mobility</p>
          <h1 id="landing-title">독수리 택시</h1>
          <p className="hero-line">
            유사한 조건을 가진 학생들끼리 파티를 구성할 수 있도록 도와주는 택시 합승 중개 플랫폼
          </p>
          <div className="hero-eagle-signal">
            <EagleMark small />
            <span>독수리처럼 빠르게, 같은 방향의 학생을 연결합니다.</span>
          </div>
          <div className="hero-buttons">
            <button className="solid-button large" type="button" onClick={() => navigate(startRoute)}>
              시작하기
              <ArrowRight size={19} />
            </button>
            <a className="outline-link" href="#problem">배경과 해결 방식 보기</a>
          </div>
        </div>

        <section className="hero-step-loop" aria-label="사용 방법 단계 자동 전환">
          <div className="loop-header">
            <div>
              <p>How it works</p>
              <strong>사용 흐름</strong>
            </div>
            <span>Auto loop</span>
          </div>

          <div className="loop-stage">
            {HERO_STEPS.map(([step, title, text], index) => (
              <article className="loop-card" key={step} style={{ '--delay': `${index * 4}s` }}>
                <span>{step}</span>
                <h2>{title}</h2>
                <p>{text}</p>
              </article>
            ))}
          </div>

          <div className="loop-dots" aria-hidden="true">
            {HERO_STEPS.map(([step], index) => (
              <i key={step} style={{ '--delay': `${index * 4}s` }} />
            ))}
          </div>
        </section>
      </section>

      <section className="problem-band context-band" id="problem">
        <div className="section-heading">
          <p className="eyebrow">서비스 배경과 해결 방식</p>
          <h2>이동 부담을 함께 줄입니다.</h2>
        </div>

        <div className="context-grid">
          <div className="context-copy">
            <p className="context-lead">
              연세대학교 미래캠퍼스는 기숙사생 비율이 높아 원주역과 원주고속버스터미널을 오가는
              학생이 많습니다. 하지만 두 교통 거점은 캠퍼스에서 차로 약 20분 떨어져 있고,
              버스 노선과 배차 간격도 제한적입니다.
            </p>
            <p>
              정해진 시간에 맞춰 이동해야 하는 학생들은 택시를 자주 선택하게 되고, 반복되는 택시비는
              부담이 됩니다. 독수리 택시는 이 부담을 나누기 위해 같은 이동 조건의 학생들을 연결합니다.
            </p>
          </div>
          <BusChart />
        </div>

        <div className="solution-panel">
          <h3>같은 조건의 학생들의 합승과 비용 분담을 돕습니다.</h3>
          <div className="solution-flow">
            {SOLUTION_FLOW.map(([title, text], index) => (
              <article className="flow-card" key={title}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <strong>{title}</strong>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="feature-band" id="features">
        <div className="section-heading compact">
          <p className="eyebrow">주요 기능</p>
          <h2>파티를 찾고 만드는 기능</h2>
        </div>
        <div className="feature-grid">
          {FEATURES.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>
      </section>

      <section className="usage-band" id="usage">
        <div className="usage-title">
          <h2>사용 방법</h2>
          <p>
            파티 생성, 검색, 참여, 요금 확인 순서로 이용합니다. 실제 택시 호출과 결제 수단 등록은
            MVP 수준에서는 구현하지 않습니다.
          </p>
        </div>
        <div className="step-grid">
          <StepCard step="Step. 1" title="1단계: 사용자 정보 입력" text="이름, 성별, 학교 이메일, 비밀번호를 입력해 계정을 생성합니다." />
          <StepCard step="Step. 2" title="2단계: 택시 파티 생성 & 조회" text="출발지, 목적지, 출발 시간, 희망 성별을 입력하고 모집 중인 파티를 확인합니다." />
          <StepCard step="Step. 3" title="3단계: 택시 파티 참가" text="조건이 맞는 파티에 참여합니다." />
          <StepCard step="Step. 4" title="4단계: 택시 이용 & 분할 결제" text="매칭 완료된 파티원끼리 정해진 시간과 장소에서 만나 택시를 이용합니다. 실제 분할 결제는 MVP 수준에서는 구현하지 않습니다." />
        </div>
      </section>

      <footer className="team-footer">
        <div>
          <strong>6팀 Mirae Mobility</strong>
          <span>독수리 택시</span>
        </div>
        <div className="team-role-list">
          {TEAM_ROLES.map((member) => (
            <p key={member.name}>
              <span>{member.role}</span>
              <strong>{member.name}</strong>
            </p>
          ))}
        </div>
        <p>연세대학교 미래캠퍼스 컴퓨팅사고(YHX1001.07-00) 프로젝트 6팀 Mirae Mobility</p>
      </footer>
    </main>
  );
}
