import BrandName from './BrandName';
import EagleMark from './EagleMark';
import { VERSION } from '../constants/team';

const FOOTER_LINKS = [
  { path: '/terms', label: '이용약관' },
  { path: '/privacy', label: '개인정보 처리방침' },
  { path: '/guide', label: '이용 안내' },
];

export default function SystemFooter({ navigate }) {
  return (
    <footer className="system-footer">
      <div className="system-footer-brand">
        <button className="brand-button" type="button" onClick={() => navigate('/')}>
          <EagleMark small />
          <BrandName />
        </button>
        <span>v{VERSION}</span>
      </div>

      <div className="system-footer-links">
        <p>Copyright 2026 Mirae Mobility. All rights reserved.</p>
        <nav aria-label="서비스 문서">
          {FOOTER_LINKS.map((link) => (
            <button key={link.path} type="button" onClick={() => navigate(link.path)}>
              {link.label}
            </button>
          ))}
        </nav>
      </div>
    </footer>
  );
}
