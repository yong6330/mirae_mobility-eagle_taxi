import {
  ClipboardList,
  Home,
  LogOut,
  MapPinned,
  Moon,
  Plus,
  Search,
  Shield,
  Sun,
  UserRoundCog,
} from 'lucide-react';
import EagleMark from './EagleMark';

const NAV_ITEMS = [
  { path: '/main', label: '메인', icon: Home },
  { path: '/parties', label: '파티 찾기', icon: Search },
  { path: '/parties/new', label: '파티 만들기', icon: Plus },
  { path: '/my/parties', label: '내 파티', icon: ClipboardList },
  { path: '/guide', label: '안전 안내', icon: Shield },
  { path: '/settings', label: '설정', icon: UserRoundCog },
];

export default function AppLayout({
  children,
  currentPath,
  isDark,
  navigate,
  onLogout,
  onToggleTheme,
  user,
}) {
  return (
    <main className="workspace-page">
      <header className="workspace-header">
        <button className="brand-button" type="button" onClick={() => navigate(user ? '/main' : '/')}>
          <EagleMark small />
          <span>독수리 택시</span>
        </button>

        <nav className="workspace-nav" aria-label="앱 주요 화면">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const selected =
              item.path === '/parties'
                ? currentPath === '/parties' || /^\/parties\/[^/]+(\/chat)?$/.test(currentPath)
                : currentPath === item.path || currentPath.startsWith(`${item.path}/`);
            return (
              <button
                className={selected ? 'selected' : ''}
                key={item.path}
                type="button"
                onClick={() => navigate(item.path)}
              >
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
          {user?.role === 'admin' && (
            <button
              className={currentPath === '/admin' ? 'selected' : ''}
              type="button"
              onClick={() => navigate('/admin')}
            >
              <MapPinned size={16} />
              관리자
            </button>
          )}
        </nav>

        <div className="header-actions">
          <button className="icon-button" type="button" onClick={onToggleTheme} aria-label="테마 전환">
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          {user ? (
            <button className="quiet-button" type="button" onClick={onLogout}>
              <LogOut size={17} />
              로그아웃
            </button>
          ) : (
            <>
              <button className="quiet-button" type="button" onClick={() => navigate('/login')}>
                로그인
              </button>
              <button className="solid-button" type="button" onClick={() => navigate('/signup')}>
                회원가입
              </button>
            </>
          )}
        </div>
      </header>

      <section className="workspace-shell">
        {children}
      </section>
    </main>
  );
}
