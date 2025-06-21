import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TMDBService:
    """TMDB API와 연동하는 서비스 클래스"""

    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base_url = "https://image.tmdb.org/t/p/w500"

        if not self.api_key:
            raise ValueError("TMDB_API_KEY가 설정되지 않았습니다.")

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """TMDB API 요청을 보내는 기본 메서드"""
        if params is None:
            params = {}

        params.update({
            'api_key': self.api_key,
            'language': 'ko-KR'  # 한국어 결과
        })

        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API 요청 실패: {e}")
            return None

    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """영화 검색"""
        if not query.strip():
            return None

        params = {
            'query': query,
            'page': page,
            'include_adult': False  # 성인 콘텐츠 제외
        }

        return self._make_request('search/movie', params)

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """영화 상세 정보 조회"""
        return self._make_request(f'movie/{movie_id}')

    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """인기 영화 목록 조회"""
        params = {'page': page}
        return self._make_request('movie/popular', params)

    def get_movie_genres(self) -> Optional[Dict]:
        """영화 장르 목록 조회"""
        return self._make_request('genre/movie/list')


class MovieCategoryMapper:
    """영화 장르를 MOVIE 모델 카테고리로 매핑하는 클래스"""

    # TMDB 장르 ID와 우리 카테고리 매핑
    GENRE_MAPPINGS = {
        # 멜로드라마 (Melodrama)
        'melodrama': [18, 10749, 10402],  # Drama, Romance, Music

        # 코미디 (Comic)
        'comic': [35, 16, 10751],  # Comedy, Animation, Family

        # 폭력적 (Violent)
        'violent': [28, 10752, 37, 53],  # Action, War, Western, Thriller

        # 상상력 (Imaginative)
        'imaginative': [12, 14, 878],  # Adventure, Fantasy, Science Fiction

        # 스릴러/공포 (Exciting)
        'exciting': [27, 9648, 80]  # Horror, Mystery, Crime
    }

    @classmethod
    def calculate_category_scores(cls, genre_ids: List[int]) -> Dict[str, float]:
        """장르 ID 목록을 받아서 카테고리별 점수 계산"""
        scores = {
            'melodrama_score': 0.0,
            'comic_score': 0.0,
            'violent_score': 0.0,
            'imaginative_score': 0.0,
            'exciting_score': 0.0
        }

        if not genre_ids:
            return scores

        total_genres = len(genre_ids)

        for category, mapped_genres in cls.GENRE_MAPPINGS.items():
            matching_genres = set(genre_ids) & set(mapped_genres)
            score = len(matching_genres) / total_genres
            scores[f'{category}_score'] = score

        return scores

    @classmethod
    def get_primary_category(cls, genre_ids: List[int]) -> str:
        """주요 카테고리 반환"""
        scores = cls.calculate_category_scores(genre_ids)
        max_category = max(scores, key=scores.get)
        return max_category.replace('_score', '')