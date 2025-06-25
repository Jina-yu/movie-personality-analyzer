// src/components/common/AuthCheck.js 수정
import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const AuthCheck = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorDetails, setErrorDetails] = useState('');

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      console.log('🔍 인증 상태 확인 시작...');

      // 검색 결과[4] 패턴: 상세한 에러 정보 수집
      const response = await api.get('/api/preferences/');
      console.log('✅ 인증 성공:', response.status);
      setIsAuthenticated(true);
      setErrorDetails('');

    } catch (error) {
      console.error('❌ 인증 실패:', error);

      // 검색 결과[4] 기반 상세한 에러 분석
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;

        if (status === 403) {
          if (data?.detail?.includes('Authentication credentials')) {
            setErrorDetails('인증 정보가 제공되지 않았습니다. Django Admin에서 로그인 후 브라우저를 새로고침해주세요.');
          } else if (data?.detail?.includes('CSRF')) {
            setErrorDetails('CSRF 토큰 문제입니다. 브라우저 쿠키를 정리하고 다시 시도해주세요.');
          } else {
            setErrorDetails(`403 Forbidden: ${data?.detail || '권한이 없습니다'}`);
          }
        } else {
          setErrorDetails(`HTTP ${status}: ${data?.detail || error.message}`);
        }
      } else {
        setErrorDetails('서버에 연결할 수 없습니다. Django 서버가 실행 중인지 확인해주세요.');
      }

      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleClearCache = () => {
    // 브라우저 캐시와 쿠키 정리 안내
    alert(`다음 단계를 따라해주세요:
    
1. F12 → Application 탭 → Storage
2. Cookies → localhost, 127.0.0.1 모두 삭제
3. Local Storage, Session Storage 삭제
4. 브라우저 새로고침`);
  };

  const handleLogin = () => {
    // localhost로 통일된 URL 사용
    window.open('http://localhost:8000/admin/', '_blank');
  };

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: 'var(--spacing-xl)' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h2>🔄 인증 상태 확인 중...</h2>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            Django 서버와 연결을 확인하고 있습니다.
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="container" style={{ paddingTop: 'var(--spacing-xl)' }}>
        <div className="card" style={{
          textAlign: 'center',
          border: '2px solid var(--color-accent-primary)',
          background: 'rgba(229, 9, 20, 0.1)'
        }}>
          <h2 style={{ color: 'var(--color-accent-primary)', marginBottom: 'var(--spacing-md)' }}>
            🔐 인증 문제 발생
          </h2>

          <div style={{
            background: 'rgba(255,255,255,0.05)',
            padding: 'var(--spacing-md)',
            borderRadius: 'var(--radius-small)',
            marginBottom: 'var(--spacing-lg)',
            fontSize: 'var(--font-size-sm)'
          }}>
            <p style={{ color: 'var(--color-text-primary)' }}>
              <strong>오류 상세:</strong> {errorDetails}
            </p>
          </div>

          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
            <button onClick={handleLogin} className="btn-primary" style={{ marginRight: 'var(--spacing-md)' }}>
              🔗 Django Admin 로그인
            </button>
            <button onClick={handleClearCache} className="btn-primary" style={{ marginRight: 'var(--spacing-md)' }}>
              🧹 캐시 정리 방법
            </button>
            <button onClick={() => { setLoading(true); checkAuthStatus(); }} className="btn-primary">
              🔄 다시 확인
            </button>
          </div>

          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            <p>💡 <strong>권장 해결 순서:</strong></p>
            <p>1. Django Admin 로그인 (localhost:8000/admin)</p>
            <p>2. 브라우저 캐시/쿠키 정리</p>
            <p>3. 이 페이지에서 "다시 확인" 클릭</p>
          </div>
        </div>
      </div>
    );
  }

  return children;
};

export default AuthCheck;
