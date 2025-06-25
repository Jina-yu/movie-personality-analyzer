import React, { useState } from 'react';
import { searchMovies, searchAndSaveMovies } from '../../services/movieService';

const MovieSearch = ({ onSearchResults, loading, setLoading }) => {
  const [query, setQuery] = useState('');
  const [message, setMessage] = useState('');

  // 검색 결과[1] 패턴: async/await와 try-catch 사용
  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setMessage('검색어를 입력해주세요.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      // 1단계: 기존 영화 검색
      let results = await searchMovies(query);

      // 2단계: 결과가 없으면 TMDB에서 검색 후 저장
      if (!results.results || results.results.length === 0) {
        setMessage('TMDB에서 새로운 영화를 검색 중...');
        const savedResults = await searchAndSaveMovies(query);

        if (savedResults.movies && savedResults.movies.length > 0) {
          results = { results: savedResults.movies };
          setMessage(`✅ ${savedResults.message}`);
        } else {
          setMessage('검색 결과가 없습니다. 다른 검색어를 시도해보세요.');
          results = { results: [] };
        }
      } else {
        setMessage(`✅ ${results.results.length}개의 영화를 찾았습니다.`);
      }

      onSearchResults(results.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setMessage(`❌ 검색 중 오류가 발생했습니다: ${error.message}`);
      onSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginBottom: 'var(--spacing-xl)' }}>
      {/* 검색 폼 - 검색 결과[1] UI 패턴 참고 */}
      <form
        onSubmit={handleSearch}
        style={{
          display: 'flex',
          gap: 'var(--spacing-sm)',
          marginBottom: 'var(--spacing-md)',
          maxWidth: '600px',
          margin: '0 auto'
        }}
      >
        <input
          type="text"
          placeholder="영화 제목을 검색해보세요... (예: 기생충, 어벤져스)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            flex: 1,
            padding: 'var(--spacing-md)',
            borderRadius: 'var(--radius-medium)',
            border: '2px solid var(--color-text-secondary)',
            background: 'var(--color-bg-secondary)',
            color: 'var(--color-text-primary)',
            fontSize: 'var(--font-size-base)',
            outline: 'none',
            transition: 'all var(--transition-normal)'
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--color-accent-primary)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--color-text-secondary)'}
        />
        <button
          type="submit"
          className="btn-primary"
          disabled={loading}
          style={{
            minWidth: '120px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 'var(--spacing-sm)'
          }}
        >
          {loading ? '🔄' : '🔍'}
          {loading ? '검색 중...' : '검색'}
        </button>
      </form>

      {/* 메시지 표시 - 검색 결과[1] 패턴 */}
      {message && (
        <div style={{
          padding: 'var(--spacing-md)',
          borderRadius: 'var(--radius-small)',
          background: message.includes('❌')
            ? 'rgba(229, 9, 20, 0.1)'
            : 'rgba(70, 211, 105, 0.1)',
          border: `1px solid ${message.includes('❌') 
            ? 'var(--color-accent-primary)' 
            : 'var(--color-success)'}`,
          color: message.includes('❌')
            ? 'var(--color-accent-primary)'
            : 'var(--color-success)',
          textAlign: 'center',
          maxWidth: '600px',
          margin: '0 auto'
        }}>
          {message}
        </div>
      )}
    </div>
  );
};

export default MovieSearch;
