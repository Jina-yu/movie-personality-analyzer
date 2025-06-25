import React, { useState, useEffect } from 'react';
import PersonalityRadarChart from '../components/charts/PersonalityRadarChart';
import ValuesBarChart from '../components/charts/ValuesBarChart';
import { getLatestAnalysis } from '../services/analysisService';

const PersonalityResults = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalysisResults();
  }, []);

  const loadAnalysisResults = async () => {
    try {
      console.log('🔍 분석 결과 로딩 중...');
      const data = await getLatestAnalysis();
      console.log('📊 받은 분석 데이터 (전체):', data);

      setAnalysisData(data);
    } catch (err) {
      console.error('❌ 분석 결과 로드 실패:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: 'var(--spacing-xl)' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h2>🧠 성격 분석 결과 로딩 중...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" style={{ paddingTop: 'var(--spacing-xl)' }}>
        <div className="card" style={{
          textAlign: 'center',
          border: '2px solid var(--color-accent-primary)',
          background: 'rgba(229, 9, 20, 0.1)'
        }}>
          <h2 style={{ color: 'var(--color-accent-primary)' }}>
            ❌ 분석 결과를 불러올 수 없습니다
          </h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  // 검색 결과 [4] 패턴: 안전한 데이터 추출
  console.log('🎯 전체 분석 데이터:', analysisData);

  // Network 탭에서 확인한 정확한 구조에 맞게 추출
  const confidence = analysisData?.confidence || 0;
  const message = analysisData?.message || '';
  const personality = analysisData?.data?.personality || {};
  const values = analysisData?.data?.values || {};

  // 검색 결과 [4]의 정규식 패턴: 메시지에서 영화 수 추출
  const movieCountMatch = message.match(/(\d+)편/);
  const moviesAnalyzed = movieCountMatch ? movieCountMatch[1] : '5';

  console.log('📈 추출된 개별 데이터:');
  console.log('- 원본 신뢰도:', confidence);
  console.log('- 신뢰도 퍼센트:', (confidence * 100).toFixed(0));
  console.log('- 원본 메시지:', message);
  console.log('- 추출된 영화 수:', moviesAnalyzed);
  console.log('- 성격 데이터:', personality);
  console.log('- 가치관 데이터:', values);

  return (
    <div className="container" style={{ paddingTop: 'var(--spacing-xl)' }}>
      {/* 헤더 */}
      <header style={{ textAlign: 'center', marginBottom: 'var(--spacing-2xl)' }}>
        <h1 style={{
          fontSize: 'var(--font-size-3xl)',
          fontWeight: '700',
          marginBottom: 'var(--spacing-md)',
          color: 'var(--color-text-primary)'
        }}>
          🎭 당신의 성격 분석 결과
        </h1>
        <p style={{
          fontSize: 'var(--font-size-lg)',
          color: 'var(--color-text-secondary)'
        }}>
          {moviesAnalyzed}편의 영화를 분석하여 도출된 결과입니다
        </p>
      </header>

      {/* 디버깅 정보 카드 (임시) */}
      <div className="card" style={{
        marginBottom: 'var(--spacing-lg)',
        background: 'rgba(255, 255, 0, 0.1)',
        border: '1px solid yellow'
      }}>
        <h3 style={{ color: 'yellow', marginBottom: 'var(--spacing-md)' }}>
          🔍 실시간 데이터 확인 (개발용)
        </h3>
        <div style={{
          fontSize: '14px',
          fontFamily: 'monospace',
          color: 'white'
        }}>
          <p><strong>API 신뢰도 값:</strong> {confidence}</p>
          <p><strong>계산된 퍼센트:</strong> {(confidence * 100).toFixed(0)}%</p>
          <p><strong>원본 메시지:</strong> "{message}"</p>
          <p><strong>추출된 영화 수:</strong> {moviesAnalyzed}편</p>
          <p><strong>성격 데이터 존재:</strong> {Object.keys(personality).length > 0 ? '✅' : '❌'}</p>
          <p><strong>가치관 데이터 존재:</strong> {Object.keys(values).length > 0 ? '✅' : '❌'}</p>
        </div>
      </div>

      {/* 성격 요약 카드 */}
      <div className="card" style={{
        textAlign: 'center',
        marginBottom: 'var(--spacing-2xl)',
        background: 'var(--gradient-card)',
        border: '2px solid var(--color-accent-primary)'
      }}>
        <h2 style={{
          fontSize: 'var(--font-size-xl)',
          marginBottom: 'var(--spacing-md)',
          color: 'var(--color-accent-primary)'
        }}>
          🎉 성격 분석 완료!
        </h2>

        {message && (
          <p style={{
            color: 'var(--color-text-secondary)',
            marginBottom: 'var(--spacing-md)',
            fontSize: 'var(--font-size-base)'
          }}>
            {message}
          </p>
        )}

        <div style={{
          fontSize: 'var(--font-size-lg)',
          marginBottom: 'var(--spacing-lg)'
        }}>
          신뢰도: <span style={{
            color: 'var(--color-success)',
            fontWeight: '700',
            fontSize: 'var(--font-size-xl)'
          }}>
            {(confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Big Five 레이더 차트 */}
      <div className="card" style={{ marginBottom: 'var(--spacing-2xl)' }}>
        <h3 style={{
          fontSize: 'var(--font-size-xl)',
          marginBottom: 'var(--spacing-lg)',
          color: 'var(--color-text-primary)',
          textAlign: 'center'
        }}>
          📊 성격 특성 분석 (Big Five)
        </h3>
        <PersonalityRadarChart personalityData={personality} size={400} />

        {/* 성격 수치 표시 */}
        {Object.keys(personality).length > 0 && (
          <div style={{
            marginTop: 'var(--spacing-lg)',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: 'var(--spacing-sm)',
            fontSize: 'var(--font-size-sm)',
            textAlign: 'center'
          }}>
            <div>개방성: {((personality?.openness || 0) * 100).toFixed(0)}점</div>
            <div>성실성: {((personality?.conscientiousness || 0) * 100).toFixed(0)}점</div>
            <div>외향성: {((personality?.extraversion || 0) * 100).toFixed(0)}점</div>
            <div>친화성: {((personality?.agreeableness || 0) * 100).toFixed(0)}점</div>
            <div>신경성: {((personality?.neuroticism || 0) * 100).toFixed(0)}점</div>
          </div>
        )}
      </div>

      {/* 가치관 막대 차트 */}
      <div className="card" style={{ marginBottom: 'var(--spacing-2xl)' }}>
        <h3 style={{
          fontSize: 'var(--font-size-xl)',
          marginBottom: 'var(--spacing-lg)',
          color: 'var(--color-text-primary)',
          textAlign: 'center'
        }}>
          💎 핵심 가치관 분석
        </h3>
        <ValuesBarChart valuesData={values} />
      </div>

      {/* 액션 버튼들 */}
      <div style={{
        textAlign: 'center',
        padding: 'var(--spacing-xl) 0'
      }}>
        <button className="btn-primary" style={{ marginRight: 'var(--spacing-md)' }}>
          🎬 추천 영화 보기
        </button>
        <button className="btn-primary" onClick={() => window.location.reload()}>
          🔄 다시 분석하기
        </button>
      </div>
    </div>
  );
};

export default PersonalityResults;
