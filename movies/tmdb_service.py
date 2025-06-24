# movies/tmdb_service.py 완전한 파일
import requests
from django.conf import settings
from .models import Movie, Genre
from django.core.cache import cache


class TMDBService:
    def __init__(self):
        self.api_key = getattr(settings, 'TMDB_API_KEY', '')
        self.base_url = 'https://api.themoviedb.org/3'
        self.image_base_url = 'https://image.tmdb.org/t/p/w500'

        if not self.api_key:
            print("❌ 경고: TMDB_API_KEY가 설정되지 않았습니다!")
        else:
            print(f"✅ TMDB API 키 로드됨: {len(self.api_key)} 문자")

    def search_movies(self, query, page=1, language='ko-KR'):
        """TMDB 영화 검색"""
        if not self.api_key:
            print("❌ API 키가 없어서 검색할 수 없습니다!")
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
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"✅ TMDB 검색 성공: {len(results)}개 결과")
                return results
            else:
                print(f"❌ TMDB API 오류: {response.status_code}")
                return []
        except requests.RequestException as e:
            print(f"❌ TMDB 요청 실패: {e}")
            return []

    # ✅ 누락된 get_popular_movies 메서드 추가 (검색 결과 [2] 패턴)
    def get_popular_movies(self, page=1, language='ko-KR'):
        """TMDB 인기 영화 목록 가져오기"""
        if not self.api_key:
            print("❌ API 키가 없어서 인기 영화를 가져올 수 없습니다!")
            return []

        url = f"{self.base_url}/movie/popular"
        params = {
            'api_key': self.api_key,
            'language': language,
            'page': page,
            'region': 'KR'
        }

        try:
            print(f"🔥 TMDB 인기 영화 API 호출: 페이지 {page}")
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"✅ 인기 영화 로드 성공: {len(results)}개")
                return results
            else:
                print(f"❌ 인기 영화 API 오류: {response.status_code}")
                return []

        except requests.RequestException as e:
            print(f"❌ 인기 영화 요청 실패: {e}")
            return []

    # ✅ get_top_rated_movies 메서드도 추가
    def get_top_rated_movies(self, page=1, language='ko-KR'):
        """TMDB 높은 평점 영화 목록"""
        if not self.api_key:
            return []

        url = f"{self.base_url}/movie/top_rated"
        params = {
            'api_key': self.api_key,
            'language': language,
            'page': page,
            'region': 'KR'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"✅ 높은 평점 영화 로드: {len(results)}개")
                return results
            return []
        except requests.RequestException as e:
            print(f"❌ 높은 평점 영화 요청 실패: {e}")
            return []

    def search_movies_bilingual(self, query, page=1):
        """한국어/영어 이중 검색 - genre_ids 포함 확인"""
        print(f"🌏 이중 언어 검색: '{query}'")

        # 한국어로 검색
        korean_results = self.search_movies(query, page, 'ko-KR')

        # 한국어 결과가 부족하면 영어로도 검색
        if len(korean_results) < 5:
            print(f"🔄 한국어 결과 부족 ({len(korean_results)}개), 영어 검색 추가 실행")
            english_results = self.search_movies(query, page, 'en-US')

            existing_ids = {movie['id'] for movie in korean_results}
            for movie in english_results:
                if movie['id'] not in existing_ids and len(korean_results) < 20:
                    korean_results.append(movie)

        # 🎭 첫 번째 영화의 장르 정보 로깅
        if korean_results:
            first_movie = korean_results[0]
            print(f"🎬 첫 번째 검색 결과 '{first_movie.get('title')}' genre_ids: {first_movie.get('genre_ids')}")

        print(f"📊 최종 검색 결과: {len(korean_results)}개")
        return korean_results

    def get_movie_details(self, tmdb_id):
        """영화 상세 정보 (장르 포함)"""
        if not self.api_key:
            return None

        url = f"{self.base_url}/movie/{tmdb_id}"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"🎬 영화 상세: {data.get('title')} - 장르: {len(data.get('genres', []))}개")
                return data
            return None
        except requests.RequestException as e:
            print(f"❌ 영화 상세 정보 오류: {e}")
            return None

    def get_genres(self):
        """검색 결과 [4] 패턴: 캐싱을 적용한 장르 목록 가져오기"""
        # ✅ 캐시에서 먼저 확인 (15분 캐시)
        cache_key = 'tmdb_genres'
        cached_genres = cache.get(cache_key)

        if cached_genres:
            print(f"📚 캐시된 장르 목록 사용: {len(cached_genres)}개")
            return cached_genres

        if not self.api_key:
            return []

        url = f"{self.base_url}/genre/movie/list"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                genres = data.get('genres', [])

                # ✅ 캐시에 저장 (15분)
                cache.set(cache_key, genres, 60 * 15)
                print(f"📚 TMDB 장르 목록 로드 및 캐시: {len(genres)}개")
                return genres
        except requests.RequestException as e:
            print(f"❌ 장르 목록 실패: {e}")
        return []

    def save_movie_from_tmdb(self, tmdb_id):
        """TMDB 영화를 DB에 저장"""
        try:
            print(f"💾 TMDB 영화 저장 시작: ID {tmdb_id}")

            existing_movie = Movie.objects.filter(tmdb_id=tmdb_id).first()
            if existing_movie:
                print(f"📋 영화 이미 존재: {existing_movie.title}")
                return existing_movie

            movie_details = self.get_movie_details(tmdb_id)
            if not movie_details:
                return None

            movie = Movie.objects.create(
                tmdb_id=tmdb_id,
                title=movie_details.get('title', ''),
                original_title=movie_details.get('original_title', ''),
                overview=movie_details.get('overview', ''),
                release_date=movie_details.get('release_date') or None,
                poster_path=movie_details.get('poster_path', ''),
                backdrop_path=movie_details.get('backdrop_path', ''),
                vote_average=movie_details.get('vote_average', 0),
                vote_count=movie_details.get('vote_count', 0),
                popularity=movie_details.get('popularity', 0),
                adult=movie_details.get('adult', False),
                runtime=movie_details.get('runtime'),
            )

            if movie_details.get('genres'):
                for genre_data in movie_details['genres']:
                    genre, created = Genre.objects.get_or_create(
                        tmdb_id=genre_data['id'],
                        defaults={'name': genre_data['name']}
                    )
                    movie.genres.add(genre)

            print(f"✅ 영화 저장 완료: {movie.title}")
            return movie

        except Exception as e:
            print(f"❌ 영화 저장 실패: {e}")
            return None


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
