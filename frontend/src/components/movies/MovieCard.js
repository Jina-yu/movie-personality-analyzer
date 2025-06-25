import React from 'react';
import StarRating from './StartRating.js';

const MovieCard = ({
  movie,
  userRating = 0,
  onRatingChange,
  isEvaluated = false
}) => {

  // 검색 결과[1] 패턴: 에러 처리를 위한 이미지 로딩
  const handleImageError = (e) => {
    e.target.src = 'https://via.placeholder.com/300x450/1a1a1a/ffffff?text=No+Image';
  };

  // 검색 결과[2] 패턴: 장르 리스트 표시
  const formatGenres = (genres) => {
    if (!genres || genres.length === 0) return '장르 정보 없음';
    return genres.slice(0, 3).map(genre => genre.name || genre).join(', ');
  };

  return (
    <div
      className="card"
      style={{
        position: 'relative',
        overflow: 'hidden',
        minHeight: '400px',
        border: isEvaluated ? '2px solid var(--color-success)' : '1px solid rgba(255,255,255,0.1)'
      }}
    >
      {/* 평가 완료 배지 */}
      {isEvaluated && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'var(--color-success)',
          color: 'white',
          padding: '4px 8px',
          borderRadius: 'var(--radius-small)',
          fontSize: '12px',
          fontWeight: '600',
          zIndex: 1
        }}>
          ✓ 평가 완료
        </div>
      )}

      {/* 영화 포스터 */}
      <div style={{
        width: '100%',
        height: '250px',
        overflow: 'hidden',
        borderRadius: 'var(--radius-small)',
        marginBottom: 'var(--spacing-md)'
      }}>
        <img
          src={movie.poster_url || `https://via.placeholder.com/300x450/1a1a1a/ffffff?text=${encodeURIComponent(movie.title)}`}
          alt={movie.title}
          onError={handleImageError}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transition: 'transform var(--transition-normal)'
          }}
          onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
        />
      </div>

      {/* 영화 정보 */}
      <div style={{ flex: 1 }}>
        <h3 style={{
          fontSize: 'var(--font-size-lg)',
          fontWeight: '600',
          marginBottom: 'var(--spacing-sm)',
          color: 'var(--color-text-primary)',
          lineHeight: '1.3',
          height: '2.6em',
          overflow: 'hidden',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical'
        }}>
          {movie.title}
        </h3>

        <p style={{
          color: 'var(--color-text-secondary)',
          fontSize: 'var(--font-size-sm)',
          marginBottom: 'var(--spacing-sm)'
        }}>
          {movie.release_date ? new Date(movie.release_date).getFullYear() : '년도 미상'} •
          ⭐ {movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A'}
        </p>

        <p style={{
          color: 'var(--color-text-secondary)',
          fontSize: 'var(--font-size-sm)',
          marginBottom: 'var(--spacing-md)',
          height: '2.4em',
          overflow: 'hidden',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical'
        }}>
          {formatGenres(movie.genres)}
        </p>

        {/* 별점 평가 */}
        <div style={{
          borderTop: '1px solid rgba(255,255,255,0.1)',
          paddingTop: 'var(--spacing-md)',
          marginTop: 'auto'
        }}>
          <p style={{
            fontSize: 'var(--font-size-sm)',
            marginBottom: 'var(--spacing-sm)',
            color: 'var(--color-text-secondary)'
          }}>
            이 영화를 평가해주세요:
          </p>
          <StarRating
            value={userRating}
            onChange={onRatingChange}
            size={20}
          />
        </div>
      </div>
    </div>
  );
};

export default MovieCard;
