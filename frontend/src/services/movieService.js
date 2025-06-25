import api from './api';

// 검색 결과[1] 기반: 올바른 함수 export
export const getMovies = (params = {}) => {
  return api.get('/api/movies/', { params })
    .then(response => response.data)
    .catch(error => {
      throw new Error(`영화 목록 조회 실패: ${error.message}`);
    });
};

export const searchMovies = (query) => {
  return api.get('/api/movies/', {
    params: { search: query }
  })
    .then(response => response.data)
    .catch(error => {
      throw new Error(`영화 검색 실패: ${error.message}`);
    });
};

export const searchAndSaveMovies = (query) => {
  return api.post('/api/movies/search_and_save/', { query })
    .then(response => response.data)
    .catch(error => {
      throw new Error(`영화 저장 실패: ${error.message}`);
    });
};

export const getUserPreferences = () => {
  return api.get('/api/preferences/')
    .then(response => response.data)
    .catch(error => {
      throw new Error(`선호도 조회 실패: ${error.message}`);
    });
};

export const addMoviePreference = (movieId, rating) => {
  return api.post('/api/preferences/', {
    movie_id: movieId,
    rating: rating
  })
    .then(response => response.data)
    .catch(error => {
      throw new Error(`평점 추가 실패: ${error.message}`);
    });
};
