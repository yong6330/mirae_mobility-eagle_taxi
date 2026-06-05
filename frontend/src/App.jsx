import { useEffect, useMemo, useState } from 'react';
import { api, clearToken, getToken, setToken as saveToken } from './api/client';
import AppLayout from './components/AppLayout';
import LoadingScreen from './components/LoadingScreen';
import AdminPage from './pages/AdminPage';
import AuthPage from './pages/AuthPage';
import ChatPage from './pages/ChatPage';
import GuidePage from './pages/GuidePage';
import LandingPage from './pages/LandingPage';
import LegalPage from './pages/LegalPage';
import MainPage from './pages/MainPage';
import MyPartiesPage from './pages/MyPartiesPage';
import PartiesPage from './pages/PartiesPage';
import PartyCreatePage from './pages/PartyCreatePage';
import PartyDetailPage from './pages/PartyDetailPage';
import SettingsPage from './pages/SettingsPage';
import './styles.css';

const PROTECTED_PREFIXES = ['/main', '/parties', '/my/parties', '/settings', '/admin'];

export default function App() {
  const [route, setRoute] = useState(() => window.location.pathname);
  const [booting, setBooting] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [token, setToken] = useState(() => getToken());
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState('');
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  const isAuthenticated = Boolean(token || user);

  const navigate = (nextRoute) => {
    window.history.pushState({}, '', nextRoute);
    setRoute(nextRoute);
    setMessage('');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const onPopState = () => setRoute(window.location.pathname);
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    if (route === '/register') {
      window.history.replaceState({}, '', '/signup');
      setRoute('/signup');
    }
    if (route === '/home') {
      window.history.replaceState({}, '', '/main');
      setRoute('/main');
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
        if (window.location.pathname === '/' || window.location.pathname === '/login' || window.location.pathname === '/signup') {
          navigate('/main');
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

  const handleSignup = async (payload) => {
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
      setUser(result.user || null);
      navigate('/main');
    } catch (error) {
      setMessage(error.message || '이메일 또는 비밀번호가 올바르지 않습니다.');
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

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'));
  };

  const routeInfo = useMemo(() => parseRoute(route), [route]);

  if (booting) return <LoadingScreen />;

  if (route === '/signup') {
    if (isAuthenticated) navigate('/main');
    return (
      <AuthPage
        mode="register"
        onSubmit={handleSignup}
        submitting={submitting}
        message={message}
        navigate={navigate}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
    );
  }

  if (route === '/login') {
    if (isAuthenticated) navigate('/main');
    return (
      <AuthPage
        mode="login"
        onSubmit={handleLogin}
        submitting={submitting}
        message={message}
        navigate={navigate}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
    );
  }

  if (route === '/terms') return <LegalPage type="terms" navigate={navigate} />;
  if (route === '/privacy') return <LegalPage type="privacy" navigate={navigate} />;
  if (route === '/' || route === '') {
    return <LandingPage isAuthenticated={isAuthenticated} navigate={navigate} theme={theme} onToggleTheme={toggleTheme} />;
  }

  if (needsAuth(route) && !isAuthenticated) {
    return (
      <AuthPage
        mode="login"
        onSubmit={handleLogin}
        submitting={submitting}
        message={message || '로그인이 필요한 화면입니다.'}
        navigate={navigate}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
    );
  }

  const content = renderProtectedRoute(routeInfo, {
    navigate,
    onLogout: handleLogout,
    user,
  });

  return (
    <AppLayout
      currentPath={route}
      isDark={theme === 'dark'}
      navigate={navigate}
      onLogout={handleLogout}
      onToggleTheme={toggleTheme}
      user={user}
    >
      {content}
    </AppLayout>
  );
}

function parseRoute(pathname) {
  const clean = pathname.replace(/\/+$/, '') || '/';
  const parts = clean.split('/').filter(Boolean);
  return { clean, parts };
}

function needsAuth(pathname) {
  return PROTECTED_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

function renderProtectedRoute({ clean, parts }, props) {
  if (clean === '/main') return <MainPage {...props} />;
  if (clean === '/parties') return <PartiesPage {...props} />;
  if (clean === '/parties/new') return <PartyCreatePage {...props} />;
  if (clean === '/my/parties') return <MyPartiesPage {...props} />;
  if (clean === '/guide') return <GuidePage {...props} />;
  if (clean === '/settings') return <SettingsPage {...props} />;
  if (clean === '/admin') return <AdminPage {...props} />;
  if (parts[0] === 'parties' && parts[1] && parts[2] === 'chat') {
    return <ChatPage {...props} partyId={parts[1]} />;
  }
  if (parts[0] === 'parties' && parts[1]) {
    return <PartyDetailPage {...props} partyId={parts[1]} />;
  }
  return <MainPage {...props} />;
}
