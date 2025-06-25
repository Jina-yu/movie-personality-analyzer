import api from './api';

export const analyzePersonality = () => {
  return api.post('/api/analysis/personality/analyze/')
    .then(response => {
      console.log('분석 성공:', response.data);
      return response.data;
    })
    .catch(error => {
      console.error('분석 실패:', error);

      if (error.response?.status === 400) {
        throw new Error('분석을 위해 최소 5편의 영화 평가가 필요합니다.');
      } else if (error.response?.status === 500) {
        throw new Error('서버에서 분석 처리 중 오류가 발생했습니다.');
      } else {
        throw new Error(`성격 분석 실패: ${error.message}`);
      }
    });
};

export const getLatestAnalysis = () => {
  return api.get('/api/analysis/personality/latest/')
    .then(response => response.data)
    .catch(error => {
      if (error.response?.status === 404) {
        throw new Error('아직 분석 결과가 없습니다. 먼저 영화를 평가하고 분석을 실행해주세요.');
      } else {
        throw new Error(`분석 결과 조회 실패: ${error.message}`);
      }
    });
};

export const getAnalysisStatistics = () => {
  return api.get('/api/analysis/personality/statistics/')
    .then(response => response.data)
    .catch(error => {
      throw new Error(`분석 통계 조회 실패: ${error.message}`);
    });
};
