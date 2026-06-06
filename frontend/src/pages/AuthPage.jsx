import { useState } from 'react';
import { ArrowLeft, Moon, Sun } from 'lucide-react';
import BrandName from '../components/BrandName';
import EagleMark from '../components/EagleMark';
import FormField from '../components/FormField';
import SystemFooter from '../components/SystemFooter';
import { PRIVACY_SECTIONS, TERMS_SECTIONS } from './LegalPage';

const INITIAL_FORM = {
  name: '',
  gender: '',
  email: '',
  password: '',
};

export default function AuthPage({ mode, onSubmit, submitting, message, navigate, theme, onToggleTheme }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [formError, setFormError] = useState('');
  const [agreements, setAgreements] = useState({ terms: false, privacy: false });
  const [legalModal, setLegalModal] = useState(null);
  const isRegister = mode === 'register';
  const isDark = theme === 'dark';

  const updateForm = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (isRegister) {
      if (!form.gender) {
        setFormError('성별을 선택해 주세요.');
        return;
      }
      if (!agreements.terms || !agreements.privacy) {
        setFormError('이용약관과 개인정보 처리방침에 동의해 주세요.');
        return;
      }
      if (!form.email.trim().toLowerCase().endsWith('@yonsei.ac.kr')) {
        window.alert('현재 지원하지 않는 이메일입니다.');
        return;
      }

      setFormError('');
      onSubmit({
        name: form.name,
        gender: form.gender,
        email: form.email,
        password: form.password,
      });
      return;
    }

    setFormError('');
    onSubmit({
      email: form.email,
      password: form.password,
    });
  };

  return (
    <main className="auth-page">
      <section className="auth-layout">
        <aside className="auth-context">
          <div className="auth-brand">
            <EagleMark />
            <BrandName />
          </div>
          <h1>{isRegister ? '학교 계정으로 합승 파티를 시작합니다.' : '계정으로 접속해 파티 화면으로 이동합니다.'}</h1>
          {isRegister && <p className="auth-support-note">현재 연세대학교 학교 계정만 지원합니다.</p>}
        </aside>

        <section className="auth-card">
          <div className="auth-top">
            <button className="quiet-button" type="button" onClick={() => navigate('/')}>
              <ArrowLeft size={17} />
              처음 화면
            </button>
            <button className="icon-button" type="button" onClick={onToggleTheme} aria-label="테마 전환">
              {isDark ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>

          <p className="eyebrow">Mirae Mobility Account</p>
          <h2>{isRegister ? '회원가입' : '로그인'}</h2>

          <form className="form-stack" onSubmit={handleSubmit}>
            {isRegister && (
              <>
                <FormField
                  label="이름"
                  name="name"
                  autoComplete="name"
                  placeholder="김연세"
                  value={form.name}
                  onChange={(event) => updateForm('name', event.target.value)}
                  required
                />

                <div className="field-block">
                  <span>성별</span>
                  <div className="segmented" role="group" aria-label="성별 선택">
                    <button
                      className={form.gender === 'female' ? 'selected' : ''}
                      type="button"
                      onClick={() => updateForm('gender', 'female')}
                    >
                      여성
                    </button>
                    <button
                      className={form.gender === 'male' ? 'selected' : ''}
                      type="button"
                      onClick={() => updateForm('gender', 'male')}
                    >
                      남성
                    </button>
                  </div>
                </div>
              </>
            )}

            <FormField
              label="학교 이메일"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="name@yonsei.ac.kr"
              value={form.email}
              onChange={(event) => updateForm('email', event.target.value)}
              required
            />

            <FormField
              label="비밀번호"
              name="password"
              type="password"
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              placeholder="8자 이상"
              minLength={8}
              value={form.password}
              onChange={(event) => updateForm('password', event.target.value)}
              required
            />

            {isRegister && (
              <div className="agreement-box">
                <label>
                  <input
                    type="checkbox"
                    checked={agreements.terms}
                    onChange={(event) => setAgreements((current) => ({ ...current, terms: event.target.checked }))}
                  />
                  <span>이용약관에 동의합니다.</span>
                  <button className="text-button" type="button" onClick={() => setLegalModal('terms')}>보기</button>
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={agreements.privacy}
                    onChange={(event) => setAgreements((current) => ({ ...current, privacy: event.target.checked }))}
                  />
                  <span>개인정보 처리방침에 동의합니다.</span>
                  <button className="text-button" type="button" onClick={() => setLegalModal('privacy')}>보기</button>
                </label>
              </div>
            )}

            {(formError || message) && (
              <p className={message.includes('완료') ? 'success' : 'error'}>
                {formError || message}
              </p>
            )}

            <button className="solid-button full" type="submit" disabled={submitting}>
              {submitting ? '처리 중...' : isRegister ? '회원가입' : '로그인'}
            </button>
          </form>

          <p className="switch-link muted">
            {isRegister ? '이미 계정이 있어요. ' : '아직 계정이 없어요. '}
            <button
              className="text-button"
              type="button"
              onClick={() => navigate(isRegister ? '/login' : '/signup')}
            >
              {isRegister ? '로그인하기' : '회원가입하기'}
            </button>
          </p>
        </section>
      </section>
      {legalModal && (
        <div className="modal-backdrop legal-modal-backdrop" role="presentation">
          <section className="legal-modal-card" role="dialog" aria-modal="true" aria-labelledby="legal-modal-title">
            <div className="card-title row">
              <div>
                <p className="eyebrow">{legalModal === 'privacy' ? 'Privacy' : 'Terms'}</p>
                <h2 id="legal-modal-title">{legalModal === 'privacy' ? '개인정보 처리방침' : '이용약관'}</h2>
              </div>
              <button className="icon-button" type="button" onClick={() => setLegalModal(null)} aria-label="닫기">
                ×
              </button>
            </div>
            <div className="legal-modal-content">
              {(legalModal === 'privacy' ? PRIVACY_SECTIONS : TERMS_SECTIONS).map(([title, text]) => (
                <article key={title}>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </article>
              ))}
            </div>
          </section>
        </div>
      )}
      <SystemFooter navigate={navigate} />
    </main>
  );
}
