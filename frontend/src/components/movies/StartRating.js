import React, { useState } from 'react';

const StarRating = ({
  value = 0,
  onChange,
  maxStars = 5,
  readOnly = false,
  size = 24
}) => {
  const [hoverValue, setHoverValue] = useState(0);

  // 검색 결과[4] 패턴: 성능 최적화를 위한 별 배열 생성
  const stars = Array.from({ length: maxStars }, (_, index) => index + 1);

  const handleClick = (rating) => {
    if (!readOnly && onChange) {
      onChange(rating);
    }
  };

  const handleMouseEnter = (rating) => {
    if (!readOnly) {
      setHoverValue(rating);
    }
  };

  const handleMouseLeave = () => {
    if (!readOnly) {
      setHoverValue(0);
    }
  };

  const getStarColor = (starNumber) => {
    const currentValue = hoverValue || value;
    return starNumber <= currentValue ? '#f5c518' : '#444444';
  };

  return (
    <div style={{
      display: 'flex',
      gap: '2px',
      cursor: readOnly ? 'default' : 'pointer'
    }}>
      {stars.map((star) => (
        <span
          key={star}
          onClick={() => handleClick(star)}
          onMouseEnter={() => handleMouseEnter(star)}
          onMouseLeave={handleMouseLeave}
          style={{
            fontSize: `${size}px`,
            color: getStarColor(star),
            transition: 'all var(--transition-fast)',
            transform: hoverValue === star && !readOnly ? 'scale(1.1)' : 'scale(1)',
            cursor: readOnly ? 'default' : 'pointer'
          }}
        >
          ★
        </span>
      ))}
      <span style={{
        marginLeft: '8px',
        color: 'var(--color-text-secondary)',
        fontSize: '14px'
      }}>
        {value > 0 ? `${value}/5` : '평가하기'}
      </span>
    </div>
  );
};

export default StarRating;
