# movies/tmdb_service.py
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TMDBService:
    def __init__(self):
        self.api_key = getattr(settings, 'TMDB_API_KEY', '')
        self.base_url = 'https://api.themoviedb.org/3'
        self.image_base_url = 'https://image.tmdb.org/t/p/w500'

    def search_movies(self, query, page=1, language='ko-KR'):
        """검색 결과 [6] 패턴: 실제 TMDB 영화 검색"""
        if not self.api_key:
            print("❌ TMDB API 키가 설정되지 않았습니다!")
            return []

        url = f"{self.base_url}/search/movie"
        params = {
            'api_key': self.api_key,
            'language': language,
            'query': query,
            'page': page,
            'include_adult': False
        }

        try:
            print(f"🔍 TMDB 검색 요청: {query} (언어: {language})")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get('results', [])
            print(f"✅ TMDB 검색 결과: {len(results)}개 ({data.get('total_results', 0)}개 전체)")

            return results
        except requests.RequestException as e:
            print(f"❌ TMDB 검색 실패: {e}")
            return []

    def search_movies_bilingual(self, query, page=1):
        """검색 결과 [7] 패턴: 한국어/영어 이중 검색"""
        print(f"🌏 이중 언어 검색: '{query}'")

        # 1. 한국어로 검색
        korean_results = self.search_movies(query, page, 'ko-KR')

        # 2. 한국어 결과가 부족하면 영어로도 검색
        if len(korean_results) < 5:
            print(f"🔄 한국어 결과 부족 ({len(korean_results)}개), 영어 검색 추가 실행")
            english_results = self.search_movies(query, page, 'en-US')

            # 중복 제거하며 결합
            existing_ids = {movie['id'] for movie in korean_results}
            for movie in english_results:
                if movie['id'] not in existing_ids and len(korean_results) < 20:
                    korean_results.append(movie)

        print(f"📊 최종 검색 결과: {len(korean_results)}개")
        return korean_results

    def get_movie_details(self, tmdb_id):
        """검색 결과 [4] 패턴: 영화 상세 정보 (장르 포함)"""
        if not self.api_key:
            return None

        url = f"{self.base_url}/movie/{tmdb_id}"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR',
            'append_to_response': 'credits,videos'  # 추가 정보도 함께
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            print(f"🎬 영화 상세: {data.get('title')} - 장르: {len(data.get('genres', []))}개")
            return data
        except requests.RequestException as e:
            print(f"❌ 영화 상세 정보 실패: {e}")
            return None

    def get_genres(self):
        """검색 결과 [2], [6] 패턴: 장르 목록"""
        if not self.api_key:
            return []

        url = f"{self.base_url}/genre/movie/list"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            genres = data.get('genres', [])
            print(f"📚 TMDB 장르 목록: {len(genres)}개 로드")
            return genres
        except requests.RequestException as e:
            print(f"❌ 장르 목록 실패: {e}")
            return []


# 전역 서비스 인스턴스
tmdb_service = TMDBService()


# API 키 확인 함수
def check_tmdb_connection():
    """TMDB API 연결 상태 확인"""
    if not tmdb_service.api_key:
        print("❌ TMDB_API_KEY가 설정되지 않았습니다!")
        return False

    # 간단한 테스트 요청
    test_results = tmdb_service.search_movies("frozen", language='en-US')
    if test_results:
        print(f"✅ TMDB API 연결 성공! 테스트 결과: {len(test_results)}개")
        return True
    else:
        print("❌ TMDB API 연결 실패!")
        return False
