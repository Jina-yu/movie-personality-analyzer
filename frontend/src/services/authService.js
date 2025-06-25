import api from './api';

export function checkAuthStatus() {
  return api.get('/api/auth/user/')
    .then(response => response.data)
    .catch(error => {
      throw new Error(`인증 상태 확인 실패: ${error.message}`);
    });
}

export function getCurrentUser() {
  return api.get('/api/preferences/')  // 이미 IsAuthenticated가 필요한 엔드포인트
    .then(response => {
      console.log('✅ 인증 성공!', response.data);
      return response.data;
    })
    .catch(error => {
      console.error('❌ 인증 실패:', error);
      throw error;
    });
}
