import { useState } from 'react';
import { ArrowLeft, Moon, Sun } from 'lucide-react';
import EagleMark from '../components/EagleMark';
import FormField from '../components/FormField';

const INITIAL_FORM = {
  name: '',
  gender: '',
  email: '',
  password: '',
};

export default function AuthPage({ mode, onSubmit, submitting, message, navigate, theme, onToggleTheme }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [formError, setFormError] = useState('');
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
            <span>독수리 택시</span>
          </div>
          <h1>{isRegister ? '학생 계정으로 합승 파티를 시작합니다.' : '계정으로 접속해 파티 화면으로 이동합니다.'}</h1>
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

          <p className="eyebrow">Eagle Taxi Account</p>
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
    </main>
  );
}
