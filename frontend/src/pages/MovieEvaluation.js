import React, { useState, useEffect } from 'react';
import MovieSearch from '../components/movies/MovieSearch';
import MovieCard from '../components/movies/MovieCard';
import AuthCheck from '../components/common/AuthCheck';
import { getUserPreferences, addMoviePreference } from '../services/movieService';
import { useNavigate } from 'react-router-dom';
import { analyzePersonality } from '../services/analysisService';



const MovieEvaluation = () => {
  // 검색 결과[2] 패턴: React 상태 관리
  const [searchResults, setSearchResults] = useState([]);
  const [userRatings, setUserRatings] = useState({});
  const [evaluatedMovies, setEvaluatedMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false); // 누락된 상태 추가
  const [authError, setAuthError] = useState(null);
  const navigate = useNavigate();

  // 검색 결과[3] 패턴: useEffect로 초기 데이터 로드
  useEffect(() => {
    loadUserPreferences();
  }, []);

  const loadUserPreferences = async () => {
    try {
      setAuthError(null);
      const preferences = await getUserPreferences();

      // 인증 성공 처리
      const ratingsMap = {};
      const movies = [];

      preferences.results?.forEach(pref => {
        ratingsMap[pref.movie.id] = pref.rating;
        movies.push({
          ...pref.movie,
          userRating: pref.rating
        });
      });

      setUserRatings(ratingsMap);
      setEvaluatedMovies(movies);

    } catch (error) {
      console.error('사용자 선호도 로드 실패:', error);

      if (error.message.includes('403') || error.message.includes('Forbidden')) {
        setAuthError('인증이 필요합니다. Django Admin에서 로그인 후 브라우저를 새로고침해주세요.');
      }
    }
  };

  // 검색 결과 처리 함수 (누락된 함수 추가)
  const handleSearchResults = (movies) => {
    setSearchResults(movies);
  };

  // 별점 평가 처리 - 검색 결과[4] 패턴
  const handleRatingChange = async (movieId, rating) => {
    try {
      setLoading(true);
      setAuthError(null);

      const response = await addMoviePreference(movieId, rating);

      // 성공 처리
      setUserRatings(prev => ({
        ...prev,
        [movieId]: rating
      }));

      const movie = searchResults.find(m => m.id === movieId);
      if (movie) {
        setEvaluatedMovies(prev => {
          const existing = prev.find(m => m.id === movieId);
          if (existing) {
            return prev.map(m =>
              m.id === movieId ? { ...m, userRating: rating } : m
            );
          } else {
            return [...prev, { ...movie, userRating: rating }];
          }
        });
      }

    } catch (error) {
      console.error('평점 저장 실패:', error);

      if (error.message.includes('403') || error.message.includes('Forbidden')) {
        setAuthError('인증이 만료되었습니다. Django Admin에서 다시 로그인해주세요.');
      } else {
        alert(`평점 저장 실패: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  // 성격 분석 시작 함수 (누락된 함수 추가)
  const handleStartAnalysis = async () => {
    try {
      console.log('🧠 성격 분석 시작...');

      // 실제 분석 API 호출
      const analysisResult = await analyzePersonality();

      console.log('✅ 분석 완료:', analysisResult);

      // 성공 메시지 표시
      alert(`🎉 성격 분석이 완료되었습니다!
      
📊 분석된 영화: ${analysisResult.data?.personality?.movies_analyzed || evaluatedMovies.length}편
🎯 신뢰도: ${((analysisResult.confidence || 0) * 100).toFixed(0)}%

결과 페이지로 이동합니다!`);

      // 결과 페이지로 이동
      navigate('/results');

    } catch (error) {
      console.error('❌ 분석 실패:', error);

      // 에러 메시지 표시
      alert(`❌ 분석 중 오류가 발생했습니다:
      
${error.message}

다시 시도해주세요.`);
    } finally {
      setAnalyzing(false);
    }
  };


  // 분석 가능 여부 확인
  const canAnalyze = evaluatedMovies.length >= 5;



  // 인증 오류 표시
  if (authError) {
    return (
    <AuthCheck>
      <div className="container" style={{ paddingTop: 'var(--spacing-xl)' }}>
        <div className="card" style={{
          textAlign: 'center',
          border: '2px solid var(--color-accent-primary)',
          background: 'rgba(229, 9, 20, 0.1)'
        }}>
          <h2 style={{ color: 'var(--color-accent-primary)', marginBottom: 'var(--spacing-md)' }}>
            🔐 인증 필요
          </h2>
          <p style={{ color: 'var(--color-text-primary)', marginBottom: 'var(--spacing-lg)' }}>
            {authError}
          </p>
          <div style={{ marginBottom: 'var(--spacing-md)' }}>
            <a
              href="http://127.0.0.1:8000/admin/"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
              style={{ marginRight: 'var(--spacing-md)' }}
            >
              🔗 Django Admin 로그인
            </a>
            <button
              className="btn-primary"
              onClick={() => window.location.reload()}
            >
              🔄 페이지 새로고침
            </button>
          </div>
        </div>
      </div>
      </AuthCheck>
    );
  }

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
          🎬 영화 평가하기
        </h1>
        <p style={{
          fontSize: 'var(--font-size-lg)',
          color: 'var(--color-text-secondary)',
          marginBottom: 'var(--spacing-xl)'
        }}>
          좋아하는 영화를 최소 5편 평가해주세요!
        </p>

        {/* 진행 상황 표시 */}
        <div className="card" style={{
          background: canAnalyze
            ? 'linear-gradient(135deg, rgba(70, 211, 105, 0.1) 0%, rgba(70, 211, 105, 0.2) 100%)'
            : 'var(--gradient-card)',
          border: `2px solid ${canAnalyze ? 'var(--color-success)' : 'var(--color-accent-primary)'}`,
          maxWidth: '500px',
          margin: '0 auto',
          textAlign: 'center'
        }}>
          <h3 style={{
            color: canAnalyze ? 'var(--color-success)' : 'var(--color-accent-primary)',
            marginBottom: 'var(--spacing-sm)'
          }}>
            {canAnalyze ? '✅ 분석 준비 완료!' : '📝 평가 진행 중'}
          </h3>
          <p style={{
            fontSize: 'var(--font-size-lg)',
            fontWeight: '600',
            color: 'var(--color-text-primary)',
            marginBottom: 'var(--spacing-md)'
          }}>
            {evaluatedMovies.length} / 5편 완료
          </p>
          <div style={{
            width: '100%',
            height: '8px',
            background: 'var(--color-bg-secondary)',
            borderRadius: 'var(--radius-small)',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${Math.min((evaluatedMovies.length / 5) * 100, 100)}%`,
              height: '100%',
              background: canAnalyze
                ? 'var(--color-success)'
                : 'var(--gradient-primary)',
              transition: 'width var(--transition-normal)'
            }} />
          </div>
        </div>
      </header>

      {/* 영화 검색 */}
      <MovieSearch
        onSearchResults={handleSearchResults}
        loading={loading}
        setLoading={setLoading}
      />

      {/* 검색 결과 */}
      {searchResults.length > 0 && (
        <section style={{ marginBottom: 'var(--spacing-2xl)' }}>
          <h2 style={{
            fontSize: 'var(--font-size-xl)',
            marginBottom: 'var(--spacing-lg)',
            color: 'var(--color-text-primary)'
          }}>
            🔍 검색 결과
          </h2>
          <div className="grid-cards">
            {searchResults.map(movie => (
              <MovieCard
                key={movie.id}
                movie={movie}
                userRating={userRatings[movie.id] || 0}
                onRatingChange={(rating) => handleRatingChange(movie.id, rating)}
                isEvaluated={!!userRatings[movie.id]}
              />
            ))}
          </div>
        </section>
      )}

      {/* 평가한 영화 목록 */}
      {evaluatedMovies.length > 0 && (
        <section style={{ marginBottom: 'var(--spacing-2xl)' }}>
          <h2 style={{
            fontSize: 'var(--font-size-xl)',
            marginBottom: 'var(--spacing-lg)',
            color: 'var(--color-text-primary)'
          }}>
            ⭐ 내가 평가한 영화들
          </h2>
          <div className="grid-cards">
            {evaluatedMovies.slice(0, 6).map(movie => (
              <MovieCard
                key={movie.id}
                movie={movie}
                userRating={movie.userRating}
                onRatingChange={(rating) => handleRatingChange(movie.id, rating)}
                isEvaluated={true}
              />
            ))}
          </div>

          {evaluatedMovies.length > 6 && (
            <div style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
              <p style={{ color: 'var(--color-text-secondary)' }}>
                ... 외 {evaluatedMovies.length - 6}편 더
              </p>
            </div>
          )}
        </section>
      )}


      {/* 분석 시작 버튼 */}
      <div style={{
        textAlign: 'center',
        padding: 'var(--spacing-2xl) 0',
        borderTop: '1px solid rgba(255,255,255,0.1)'
      }}>
        <button
          className="btn-primary"
          onClick={handleStartAnalysis}
          disabled={!canAnalyze || analyzing}
          style={{
            fontSize: 'var(--font-size-lg)',
            padding: 'var(--spacing-lg) var(--spacing-2xl)',
            opacity: canAnalyze ? 1 : 0.5,
            cursor: canAnalyze ? 'pointer' : 'not-allowed'
          }}
        >
          {analyzing ? '🔄 분석 중...' :
           canAnalyze ? '🧠 성격 분석 시작하기' :
           `📝 ${5 - evaluatedMovies.length}편 더 평가해주세요`}
        </button>

        {!canAnalyze && (
          <p style={{
            color: 'var(--color-text-secondary)',
            marginTop: 'var(--spacing-md)',
            fontSize: 'var(--font-size-sm)'
          }}>
            정확한 분석을 위해 최소 5편의 영화 평가가 필요합니다
          </p>
        )}
      </div>
    </div>

  );
};

export default MovieEvaluation;
