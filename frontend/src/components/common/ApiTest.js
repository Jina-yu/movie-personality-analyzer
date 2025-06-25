import React, { useState, useEffect } from 'react';
import { getMovies, searchMovies } from '../../services/movieService';
import { getAnalysisStatistics } from '../../services/analysisService';

const ApiTest = () => {
  const [movies, setMovies] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 검색 결과[3] 패턴: useEffect로 초기 데이터 로드
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);

    try {
      // 병렬로 API 호출
      const [moviesData, statsData] = await Promise.all([
        getMovies(),
        getAnalysisStatistics().catch(() => null) // 통계는 실패해도 괜찮음
      ]);

      setMovies(moviesData.results || []);
      setStats(statsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    const query = e.target.search.value.trim();

    if (!query) return;

    setLoading(true);
    setError(null);

    try {
      const data = await searchMovies(query);
      setMovies(data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 'var(--spacing-lg)' }}>
      <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <h2>🔗 API 연동 테스트</h2>

        {/* 통계 정보 */}
        {stats && (
          <div style={{
            background: 'var(--color-bg-secondary)',
            padding: 'var(--spacing-md)',
            borderRadius: 'var(--radius-small)',
            marginBottom: 'var(--spacing-md)'
          }}>
            <h4>📊 현재 상태</h4>
            <p>평가한 영화: {stats.total_movies_rated}편</p>
            <p>분석 준비: {stats.analysis_ready ? '✅ 완료' : '❌ 부족'}</p>
          </div>
        )}

        {/* 검색 폼 */}
        <form onSubmit={handleSearch} style={{ marginBottom: 'var(--spacing-md)' }}>
          <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
            <input
              name="search"
              type="text"
              placeholder="영화 제목 검색..."
              style={{
                flex: 1,
                padding: 'var(--spacing-sm)',
                borderRadius: 'var(--radius-small)',
                border: '1px solid var(--color-text-secondary)',
                background: 'var(--color-bg-secondary)',
                color: 'var(--color-text-primary)'
              }}
            />
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? '검색 중...' : '검색'}
            </button>
          </div>
        </form>

        {/* 에러 표시 */}
        {error && (
          <div style={{
            color: 'var(--color-accent-primary)',
            marginBottom: 'var(--spacing-md)',
            padding: 'var(--spacing-sm)',
            background: 'rgba(229, 9, 20, 0.1)',
            borderRadius: 'var(--radius-small)'
          }}>
            ❌ {error}
          </div>
        )}

        {/* 로딩 상태 */}
        {loading && (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-lg)' }}>
            🔄 로딩 중...
          </div>
        )}

        {/* 영화 목록 */}
        <div className="grid-cards">
          {movies.slice(0, 6).map((movie) => (
            <div key={movie.id} className="card">
              {movie.poster_url && (
                <img
                  src={movie.poster_url}
                  alt={movie.title}
                  style={{
                    width: '100%',
                    height: '200px',
                    objectFit: 'cover',
                    borderRadius: 'var(--radius-small)',
                    marginBottom: 'var(--spacing-sm)'
                  }}
                />
              )}
              <h4>{movie.title}</h4>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
                {movie.release_date} • ⭐ {movie.vote_average}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ApiTest;
