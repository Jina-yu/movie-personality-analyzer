import React from 'react';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  const handleStartAnalysis = () => {
    navigate('/evaluate');
  };

  return (
    <div className="container">
      {/* 헤더 섹션 */}
      <header style={{
        padding: '3rem 0 2rem 0',
        textAlign: 'center'
      }}>
        <h1 style={{
          fontSize: 'var(--font-size-3xl)',
          fontWeight: '700',
          marginBottom: 'var(--spacing-md)',
          background: 'linear-gradient(135deg, #ffffff 0%, #e50914 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          🎬 MOVIE PERSONALITY
        </h1>
        <p style={{
          fontSize: 'var(--font-size-lg)',
          color: 'var(--color-text-secondary)'
        }}>
          영화로 알아보는 나의 성격 • AI 기반 Big Five 분석
        </p>
      </header>

      {/* 메인 CTA 카드 */}
      <main style={{ paddingBottom: '2rem' }}>
        <div className="card" style={{
          textAlign: 'center',
          marginBottom: 'var(--spacing-2xl)',
          background: 'var(--gradient-card)',
          border: '1px solid rgba(229, 9, 20, 0.2)'
        }}>
          <h2 style={{
            fontSize: 'var(--font-size-xl)',
            marginBottom: 'var(--spacing-md)'
          }}>
            🎭 당신만의 성격 분석을 시작하세요
          </h2>
          <p style={{
            color: 'var(--color-text-secondary)',
            marginBottom: 'var(--spacing-xl)'
          }}>
            좋아하는 영화 5편만 선택하면, 과학적으로 검증된<br/>
            Big Five 모델로 당신의 성격과 가치관을 분석해드립니다.
          </p>
          <button
            className="btn-primary"
            onClick={handleStartAnalysis}
          >
            🚀 분석 시작하기
          </button>
        </div>

        {/* 특징 카드들 */}
        <div className="grid-cards">
          <div className="card">
            <div style={{ fontSize: '2rem', marginBottom: 'var(--spacing-md)' }}>📊</div>
            <h3 style={{ fontSize: 'var(--font-size-lg)', marginBottom: 'var(--spacing-sm)' }}>
              과학적 근거
            </h3>
            <p style={{ color: 'var(--color-text-secondary)' }}>
              Big Five 성격 이론을 기반으로 한 정확하고 신뢰할 수 있는 분석 시스템
            </p>
          </div>

          <div className="card">
            <div style={{ fontSize: '2rem', marginBottom: 'var(--spacing-md)' }}>🎯</div>
            <h3 style={{ fontSize: 'var(--font-size-lg)', marginBottom: 'var(--spacing-sm)' }}>
              개인화 추천
            </h3>
            <p style={{ color: 'var(--color-text-secondary)' }}>
              분석된 성격에 맞는 영화 추천과 라이프스타일 제안까지!
            </p>
          </div>

          <div className="card">
            <div style={{ fontSize: '2rem', marginBottom: 'var(--spacing-md)' }}>🔒</div>
            <h3 style={{ fontSize: 'var(--font-size-lg)', marginBottom: 'var(--spacing-sm)' }}>
              개인정보 보호
            </h3>
            <p style={{ color: 'var(--color-text-secondary)' }}>
              모든 데이터는 안전하게 암호화되어 처리됩니다
            </p>
          </div>
        </div>

        {/* 프로세스 설명 */}
        <div style={{
          textAlign: 'center',
          marginTop: 'var(--spacing-2xl)',
          padding: 'var(--spacing-xl) 0'
        }}>
          <h3 style={{
            fontSize: 'var(--font-size-xl)',
            marginBottom: 'var(--spacing-xl)',
            color: 'var(--color-text-primary)'
          }}>
            🎬 → 👤 → 🧠 → 📊
          </h3>
          <p style={{
            color: 'var(--color-text-secondary)',
            fontSize: 'var(--font-size-base)'
          }}>
            영화 선택 → 선호도 평가 → AI 분석 → 성격 결과
          </p>
        </div>
      </main>
    </div>
  );
};

export default Home;
