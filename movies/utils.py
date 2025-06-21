from typing import List, Optional

from .models import Movie
from .services import TMDBService, MovieCategoryMapper
from django.utils.dateparse import parse_date
import logging

logger = logging.getLogger(__name__)


class MovieManager:
    """영화 데이터 관리를 위한 유틸리티 클래스"""

    def __init__(self):
        self.tmdb_service = TMDBService()

    def search_and_save_movie(self, query: str) -> List[Movie]:
        """영화를 검색하고 데이터베이스에 저장"""
        search_result = self.tmdb_service.search_movies(query)

        if not search_result or not search_result.get('results'):
            return []

        saved_movies = []

        for movie_data in search_result['results'][:5]:  # 상위 5개만 저장
            try:
                movie = self._create_or_update_movie(movie_data)
                if movie:
                    saved_movies.append(movie)
            except Exception as e:
                logger.error(f"영화 저장 중 오류: {e}")
                continue

        return saved_movies

    def _create_or_update_movie(self, movie_data: dict) -> Optional[Movie]:
        """TMDB 데이터로부터 Movie 객체 생성 또는 업데이트"""
        tmdb_id = movie_data.get('id')
        if not tmdb_id:
            return None

        # 장르 ID 목록 추출
        genre_ids = [genre['id'] for genre in movie_data.get('genres', [])]
        if not genre_ids:
            genre_ids = movie_data.get('genre_ids', [])

        # 카테고리 점수 계산
        category_scores = MovieCategoryMapper.calculate_category_scores(genre_ids)

        # 개봉일 파싱
        release_date = None
        if movie_data.get('release_date'):
            release_date = parse_date(movie_data['release_date'])

        # Movie 객체 생성 또는 업데이트
        movie, created = Movie.objects.update_or_create(
            tmdb_id=tmdb_id,
            defaults={
                'title': movie_data.get('title', ''),
                'original_title': movie_data.get('original_title', ''),
                'overview': movie_data.get('overview', ''),
                'release_date': release_date,
                'genres': movie_data.get('genres', []),
                'poster_path': movie_data.get('poster_path', ''),
                'vote_average': movie_data.get('vote_average', 0.0),
                'popularity': movie_data.get('popularity', 0.0),
                **category_scores
            }
        )

        if created:
            logger.info(f"새 영화 생성: {movie.title}")
        else:
            logger.info(f"기존 영화 업데이트: {movie.title}")

        return movie

    def get_movie_by_tmdb_id(self, tmdb_id: int) -> Optional[Movie]:
        """TMDB ID로 영화 조회"""
        try:
            return Movie.objects.get(tmdb_id=tmdb_id)
        except Movie.DoesNotExist:
            # DB에 없으면 TMDB에서 가져와서 저장
            movie_data = self.tmdb_service.get_movie_details(tmdb_id)
            if movie_data:
                return self._create_or_update_movie(movie_data)
        return None