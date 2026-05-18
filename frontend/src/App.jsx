import { useEffect, useState } from 'react';
import {
  ArrowRight,
  CalendarClock,
  CarTaxiFront,
  CheckCircle2,
  Clock3,
  Loader2,
  LogOut,
  MapPin,
  ShieldCheck,
  Users,
  WalletCards,
} from 'lucide-react';
import { api, clearToken, getToken, setToken as saveToken } from './api/client';
import './styles.css';

const VERSION = 'v0.1.0-alpha';
const TEAM_ROLES = [
  { role: 'PM / 프로젝트 총괄', name: '용석희' },
  { role: 'OM / 운영 총괄', name: '최우진' },
  { role: 'TL / 백엔드 및 종합', name: '이가람' },
  { role: 'QA&Front / 품질 및 프론트엔드', name: '심지수' },
];

export default function App() {
  const [route, setRoute] = useState(() => window.location.pathname);
  const [booting, setBooting] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [token, setToken] = useState(() => getToken());
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState('');

  const navigate = (nextRoute) => {
    window.history.pushState({}, '', nextRoute);
    setRoute(nextRoute);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const onPopState = () => setRoute(window.location.pathname);
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    if (route === '/register') {
      window.history.replaceState({}, '', '/signup');
      setRoute('/signup');
    }
  }, [route]);

  useEffect(() => {
    const boot = async () => {
      if (!token) {
        setBooting(false);
        return;
      }

      try {
        const me = await api.me();
        setUser(me);
        if (window.location.pathname === '/' || window.location.pathname === '/login') {
          navigate('/home');
        }
      } catch {
        clearToken();
        setToken(null);
        setUser(null);
      } finally {
        setBooting(false);
      }
    };

    boot();
  }, [token]);

  const handleRegister = async (payload) => {
    setSubmitting(true);
    setMessage('');

    try {
      await api.register(payload);
      setMessage('회원가입이 완료되었습니다. 로그인해 주세요.');
      navigate('/login');
    } catch (error) {
      setMessage(error.message || '회원가입 API 연결을 확인해 주세요.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogin = async (payload) => {
    setSubmitting(true);
    setMessage('');

    try {
      const result = await api.login(payload);
      saveToken(result.access_token);
      setToken(result.access_token);

      try {
        const me = await api.me();
        setUser(me);
      } catch {
        setUser(null);
      }

      navigate('/home');
    } catch (error) {
      setMessage(error.message || '로그인 API 연결을 확인해 주세요.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = () => {
    clearToken();
    setToken(null);
    setUser(null);
    setMessage('');
    navigate('/login');
  };

  if (booting) return <LoadingScreen />;

  if (route === '/signup') {
    return <AuthPage mode="register" onSubmit={handleRegister} submitting={submitting} message={message} navigate={navigate} />;
  }

  if (route === '/login') {
    return <AuthPage mode="login" onSubmit={handleLogin} submitting={submitting} message={message} navigate={navigate} />;
  }

  if (route === '/home') {
    if (!token) return <AuthPage mode="login" onSubmit={handleLogin} submitting={submitting} message={message} navigate={navigate} />;
    return <Home user={user} onLogout={handleLogout} />;
  }

  return <Landing navigate={navigate} />;
}

function LoadingScreen() {
  return (
    <main className="loading-screen">
      <div className="loading-scene" aria-hidden="true">
        <CityLine compact />
        <TaxiIllustration />
      </div>
      <Loader2 className="spin" size={30} />
      <h1>독수리 택시</h1>
      <p>서비스 상태를 확인하고 있습니다.</p>
    </main>
  );
}

function Landing({ navigate }) {
  return (
    <main className="landing">
      <header className="landing-nav">
        <button className="nav-brand" onClick={() => navigate('/')}>
          <CarTaxiFront size={23} />
          <span>독수리 택시</span>
          <em>{VERSION}</em>
        </button>
        <div className="nav-actions">
          <button className="ghost" onClick={() => navigate('/login')}>로그인</button>
          <button className="primary" onClick={() => navigate('/signup')}>회원가입</button>
        </div>
      </header>

      <section className="hero" aria-labelledby="landing-title">
        <div className="hero-copy">
          <p className="eyebrow">Yonsei Mirae Mobility</p>
          <h1 id="landing-title">
            <span>독수리 택시</span>
            <em>{VERSION}</em>
          </h1>
          <p className="hero-intro">
            유사한 조건을 가진 학생들끼리 파티를 구성할 수 있도록 도와주는 택시 합승 중개 플랫폼
          </p>
          <button className="hero-start" onClick={() => navigate('/signup')}>
            시작하기
            <ArrowRight size={20} />
          </button>
        </div>

        <div className="hero-visual" aria-hidden="true">
          <CityLine compact />
          <TaxiIllustration />
          <div className="road-shadow" />
        </div>

        <CityLine />
      </section>

      <section className="problem-section" id="problem">
        <div className="problem-copy">
          <p className="eyebrow">문제 제기</p>
          <h2>캠퍼스 밖 이동은 필요하지만, 기다림이 길다.</h2>
          <p>
            연세대학교 미래캠퍼스는 원주시 흥업면에 위치해 있어 교통 인프라가 불편합니다.
            기숙사생이 많고, 고속버스터미널과 KTX 이용을 위해 원주역을 오가는 학생도 많습니다.
          </p>
          <p>
            하지만 주요 버스 노선은 30번, 34번, 34-1번 세 개뿐이며 평균 배차 시간도 약 30분입니다.
            이동 수요가 몰리는 시간에는 기다림과 택시비 부담이 함께 커집니다.
          </p>
        </div>
        <BusChart />
      </section>

      <section className="solution-section" id="solution">
        <div>
          <p className="eyebrow">해결 방식</p>
          <h2>같은 조건의 학생들이 파티를 만들고,<br />택시비를 나눕니다.</h2>
          <p>
            같은 출발지, 도착지, 출발 시간을 가진 사람들끼리 파티를 생성해서 택시를 같이 타고
            요금을 나눠서 내기 때문에 혼자 이용할 때보다 부담이 적습니다.
          </p>
        </div>
        <div className="solution-flow">
          <span>조건 등록</span>
          <ArrowRight size={18} />
          <span>파티 매칭</span>
          <ArrowRight size={18} />
          <span>요금 분담</span>
        </div>
      </section>

      <section className="feature-section" id="features">
        <div className="section-title">
          <p className="eyebrow">주요 기능</p>
          <h2>택시 합승에 필요한 흐름만 먼저 정확하게 구현합니다.</h2>
        </div>
        <div className="feature-grid">
          <Feature icon={ShieldCheck} title="회원가입·로그인" text="학생 계정을 만들고 로그인 성공 시 홈 화면으로 이동합니다." />
          <Feature icon={MapPin} title="파티 조건 입력" text="출발지, 도착지, 희망 출발 시간으로 파티 조건을 설정합니다." />
          <Feature icon={Users} title="파티 생성·조회" text="모집 중인 파티를 확인하거나 조건에 맞는 새 파티를 만들 수 있습니다." />
          <Feature icon={WalletCards} title="예상 요금 확인" text="참여 인원 기준으로 1인 예상 부담 금액을 확인합니다." />
        </div>
      </section>

      <section className="usage-section" id="usage">
        <div className="usage-head">
          <h2>독수리 택시 <span>사용 방법</span></h2>
          <p>
            파티 생성, 검색, 참여, 요금 계산을 목표로 개발하고
            실제 결제 수단 등록, 택시 호출, 분할 결제는 이번 프로젝트 MVP에 포함하지 않습니다.
          </p>
        </div>
        <div className="step-grid">
          <StepCard step="Step. 1" title="1단계: 사용자 정보 입력" text="이름, 성별, 학교 이메일, 비밀번호를 입력해 계정을 생성합니다." />
          <StepCard step="Step. 2" title="2단계: 택시 파티 생성 & 조회" text="출발지, 목적지, 출발 시간, 희망 성별을 입력하고 모집 중인 파티를 확인합니다." />
          <StepCard step="Step. 3" title="3단계: 택시 파티 참가" text="조건이 맞는 파티에 참여합니다." />
          <StepCard step="Step. 4" title="4단계: 택시 이용 & 분할 결제" text="매칭 완료된 파티원끼리 정해진 시간과 장소에서 만나 택시를 이용한 뒤, 각자 부담 금액에 맞춰 결제합니다." />
        </div>
      </section>

      <footer className="team-footer">
        <div>
          <strong>6조 - Mirae Mobility</strong>
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
        <p>컴퓨팅사고 팀 프로젝트 · 6조 Mirae Mobility</p>
      </footer>
    </main>
  );
}

function CityLine({ compact = false }) {
  return (
    <div className={`city-line ${compact ? 'compact' : ''}`}>
      <i />
      <i />
      <i />
      <i />
      <i />
      <i />
      <i />
      <i />
    </div>
  );
}

function TaxiIllustration() {
  return (
    <div className="taxi-art">
      <div className="taxi-sign">TAXI</div>
      <div className="taxi-window" />
      <div className="taxi-body" />
      <div className="taxi-grill" />
      <span />
      <span />
    </div>
  );
}

function BusChart() {
  const rows = [
    { name: '30번', runs: 32, minutes: 30 },
    { name: '34번', runs: 22.5, minutes: 40 },
    { name: '34-1번', runs: 33, minutes: 25 },
  ];

  return (
    <article className="chart-card">
      <div className="chart-title">
        <strong>시내버스 현황</strong>
      </div>
      <h3>핵심 노선은 있지만, 기다림이 길다.</h3>
      <p>평균 배차 간격은 약 30분이고 각 버스의 노선 방향이 달라 원주역, 무실동, 터미널 이동 대기가 길어집니다.</p>

      <div className="bar-chart">
        {rows.map((row) => (
          <div className="bar-row" key={row.name}>
            <span>{row.name}</span>
            <div className="bars">
              <i style={{ '--size': `${(row.runs / 40) * 100}%` }}>
                <em>{row.runs}</em>
              </i>
              <b style={{ '--size': `${(row.minutes / 40) * 100}%` }}>
                <em>{row.minutes}</em>
              </b>
            </div>
          </div>
        ))}
      </div>

      <div className="legend">
        <span><i /> 일 운행 횟수(회)</span>
        <span><b /> 평균 배차 간격(분)</span>
      </div>
      <small>*출처: 원주시 교통정보센터 시내버스 시간표</small>
    </article>
  );
}

function Feature({ icon: Icon, title, text }) {
  return (
    <article className="feature-card">
      <Icon size={24} />
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}

function StepCard({ step, title, text }) {
  return (
    <article className="step-card">
      <span>{step}</span>
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}

function AuthPage({ mode, onSubmit, submitting, message, navigate }) {
  const isRegister = mode === 'register';
  const [gender, setGender] = useState('');
  const [formError, setFormError] = useState('');

  const submit = (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(event.currentTarget).entries());

    if (isRegister && !gender) {
      setFormError('성별을 선택해 주세요.');
      return;
    }

    setFormError('');
    if (isRegister) payload.gender = gender;
    onSubmit(payload);
  };

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <button className="text-link" onClick={() => navigate('/')}>← 처음으로</button>
        <p className="eyebrow">Eagle Taxi Account</p>
        <h1>{isRegister ? '회원가입' : '로그인'}</h1>
        <p className="muted">
          {isRegister
            ? '독수리 택시 이용을 위한 기본 정보를 입력해 주세요.'
            : '계정으로 로그인하면 홈 화면으로 이동합니다.'}
        </p>

        <form className="form-stack" onSubmit={submit}>
          {isRegister && <Field name="name" label="이름" placeholder="심지수" required />}
          <Field name="email" label="이메일" type="email" placeholder="jisu@example.com" required />
          <Field name="password" label="비밀번호" type="password" placeholder="8자 이상" minLength={8} required />

          {isRegister && (
            <div className="field-block">
              <span>성별</span>
              <div className="segmented">
                <button type="button" className={gender === 'female' ? 'selected' : ''} onClick={() => setGender('female')}>여성</button>
                <button type="button" className={gender === 'male' ? 'selected' : ''} onClick={() => setGender('male')}>남성</button>
              </div>
            </div>
          )}

          {(formError || message) && <p className={message?.includes('완료') ? 'success' : 'error'}>{formError || message}</p>}

          <button className="primary full" disabled={submitting} type="submit">
            {submitting && <Loader2 className="spin" size={18} />}
            {isRegister ? '회원가입' : '로그인'}
          </button>
        </form>

        <button className="text-link switch-link" onClick={() => navigate(isRegister ? '/login' : '/signup')}>
          {isRegister ? '이미 계정이 있어요' : '계정 만들기'}
        </button>
      </section>
    </main>
  );
}

function Home({ user, onLogout }) {
  return (
    <main className="home-page">
      <header className="home-header">
        <div className="brand">
          <CarTaxiFront size={24} />
          <span>독수리 택시</span>
        </div>
        <button className="secondary" onClick={onLogout}>
          <LogOut size={18} />
          로그아웃
        </button>
      </header>

      <section className="home-panel">
        <CheckCircle2 size={34} />
        <p className="eyebrow">로그인 성공</p>
        <h1>홈 화면</h1>
        <p className="muted">파티 생성과 검색 화면을 이어서 연결할 수 있습니다.</p>

        <div className="profile-list">
          <Info label="이름" value={user?.name || '-'} />
          <Info label="이메일" value={user?.email || '-'} />
          <Info label="성별" value={user?.gender === 'female' ? '여성' : user?.gender === 'male' ? '남성' : '-'} />
          <Info label="권한" value={user?.role || '-'} />
        </div>
      </section>
    </main>
  );
}

function Field({ label, ...props }) {
  return (
    <label className="field-block">
      <span>{label}</span>
      <input {...props} />
    </label>
  );
}

function Info({ label, value }) {
  return (
    <div className="info-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
