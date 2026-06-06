import {
  ClipboardList,
  CircleHelp,
  Home,
  LogOut,
  Moon,
  Sun,
  UserRoundCog,
} from 'lucide-react';
import BrandName from './BrandName';
import EagleMark from './EagleMark';
import SystemFooter from './SystemFooter';

const NAV_ITEMS = [
  { path: '/main', label: '메인', icon: Home },
  { path: '/my/parties', label: '내 이동', icon: ClipboardList },
  { path: '/guide', label: '이용 안내', icon: CircleHelp },
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
          <BrandName />
        </button>

        <nav className="workspace-nav" aria-label="앱 주요 화면">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const selected = currentPath === item.path || currentPath.startsWith(`${item.path}/`);
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
      <SystemFooter navigate={navigate} />
    </main>
  );
}
