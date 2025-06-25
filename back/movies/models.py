from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from typing import Any, Optional, List, Dict


class Genre(models.Model):
    """영화 장르 모델 - TMDB API 연동"""
    tmdb_id = models.IntegerField(unique=True, verbose_name="TMDB 장르 ID")
    name = models.CharField(max_length=50, verbose_name="장르명")
    name_en = models.CharField(max_length=50, blank=True, verbose_name="장르명(영어)")

    class Meta:
        verbose_name = "장르"
        verbose_name_plural = "장르들"
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(models.Model):
    """영화 정보를 저장하는 모델 - TMDB API 완전 호환"""

    # TMDB에서 가져온 기본 정보
    tmdb_id = models.IntegerField(unique=True, verbose_name="TMDB ID")
    title = models.CharField(max_length=255, verbose_name="영화 제목")
    original_title = models.CharField(max_length=255, blank=True, verbose_name="원제")
    overview = models.TextField(blank=True, verbose_name="줄거리")
    release_date = models.DateField(null=True, blank=True, verbose_name="개봉일")

    # 장르 정보 (M:N 관계) - TMDB 장르와 연결
    genres = models.ManyToManyField(Genre, blank=True, verbose_name="장르들")

    # MOVIE 모델 카테고리 점수 (규칙 기반 분석용)
    melodrama_score = models.FloatField(default=0.0, verbose_name="멜로드라마 점수")
    comic_score = models.FloatField(default=0.0, verbose_name="코미디 점수")
    violent_score = models.FloatField(default=0.0, verbose_name="액션/폭력 점수")
    imaginative_score = models.FloatField(default=0.0, verbose_name="상상력 점수")
    exciting_score = models.FloatField(default=0.0, verbose_name="스릴러 점수")

    # TMDB 이미지 정보
    poster_path = models.CharField(max_length=255, blank=True, verbose_name="포스터 경로")
    backdrop_path = models.CharField(max_length=255, blank=True, verbose_name="배경 이미지 경로")

    # TMDB 메타 정보
    vote_average = models.FloatField(default=0.0, verbose_name="TMDB 평점")
    vote_count = models.IntegerField(default=0, verbose_name="투표 수")
    popularity = models.FloatField(default=0.0, verbose_name="인기도")

    # 추가 TMDB 정보
    adult = models.BooleanField(default=False, verbose_name="성인 영화")
    video = models.BooleanField(default=False, verbose_name="비디오")
    runtime = models.IntegerField(null=True, blank=True, verbose_name="상영시간(분)")

    # 시스템 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "영화"
        verbose_name_plural = "영화들"
        ordering = ['-popularity', '-vote_average']

    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'Unknown'})"

    @property
    def poster_url(self):
        """포스터 이미지 전체 URL 반환"""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return ""

    @property
    def backdrop_url(self):
        """배경 이미지 전체 URL 반환"""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return ""

    @property
    def genre_names(self):
        """장르 이름들을 리스트로 반환"""
        return [genre.name for genre in self.genres.all()]

    @property
    def genre_names_en(self):
        """영어 장르 이름들을 리스트로 반환"""
        return [genre.name_en for genre in self.genres.all() if genre.name_en]

    def get_dominant_genre(self):
        """주요 장르 반환 (첫 번째 장르)"""
        first_genre = self.genres.first()
        return first_genre.name if first_genre else "기타"

    def calculate_personality_scores(self):
        """장르 기반 성격 특성 점수 계산"""
        # 장르별 성격 특성 매핑
        genre_personality_map = {
            '액션': {'extraversion': 0.8, 'conscientiousness': 0.7, 'neuroticism': 0.4},
            '모험': {'openness': 0.8, 'extraversion': 0.7, 'neuroticism': 0.3},
            '애니메이션': {'openness': 0.9, 'agreeableness': 0.8, 'conscientiousness': 0.6},
            '코미디': {'extraversion': 0.9, 'agreeableness': 0.8, 'neuroticism': 0.2},
            '범죄': {'conscientiousness': 0.8, 'openness': 0.6, 'agreeableness': 0.4},
            '다큐멘터리': {'openness': 0.9, 'conscientiousness': 0.8, 'agreeableness': 0.7},
            '드라마': {'agreeableness': 0.8, 'openness': 0.7, 'extraversion': 0.4},
            '가족': {'agreeableness': 0.9, 'conscientiousness': 0.7, 'neuroticism': 0.2},
            '판타지': {'openness': 0.9, 'agreeableness': 0.6, 'conscientiousness': 0.5},
            '역사': {'openness': 0.8, 'conscientiousness': 0.8, 'agreeableness': 0.6},
            '공포': {'openness': 0.8, 'neuroticism': 0.7, 'agreeableness': 0.3},
            '음악': {'openness': 0.9, 'extraversion': 0.7, 'agreeableness': 0.8},
            '미스터리': {'openness': 0.8, 'conscientiousness': 0.7, 'neuroticism': 0.5},
            '로맨스': {'agreeableness': 0.9, 'extraversion': 0.6, 'neuroticism': 0.5},
            'SF': {'openness': 0.9, 'conscientiousness': 0.6, 'agreeableness': 0.5},
            '스릴러': {'openness': 0.7, 'conscientiousness': 0.6, 'neuroticism': 0.6},
            '전쟁': {'conscientiousness': 0.8, 'agreeableness': 0.4, 'neuroticism': 0.6},
            '서부': {'extraversion': 0.7, 'conscientiousness': 0.8, 'agreeableness': 0.5}
        }

        personality_scores = {
            'openness': 0.5, 'conscientiousness': 0.5, 'extraversion': 0.5,
            'agreeableness': 0.5, 'neuroticism': 0.5
        }

        # 영화의 모든 장르에 대해 점수 계산
        genre_count = 0
        for genre in self.genres.all():
            if genre.name in genre_personality_map:
                genre_scores = genre_personality_map[genre.name]
                for trait, score in genre_scores.items():
                    personality_scores[trait] += score
                genre_count += 1

        # 평균 계산
        if genre_count > 0:
            for trait in personality_scores:
                personality_scores[trait] = personality_scores[trait] / (genre_count + 1)
                # 0.1 ~ 0.9 범위로 정규화
                personality_scores[trait] = max(0.1, min(0.9, personality_scores[trait]))

        return personality_scores


class UserMoviePreference(models.Model):
    """사용자의 영화 선호도를 저장하는 모델"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="영화")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="평점 (1-5)"
    )

    # 추가 메타데이터
    watch_date = models.DateTimeField(null=True, blank=True, verbose_name="관람일")
    review = models.TextField(blank=True, verbose_name="리뷰")
    is_favorite = models.BooleanField(default=False, verbose_name="즐겨찾기")

    # 시스템 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="평가일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        unique_together = ['user', 'movie']  # 한 사용자는 같은 영화에 한 번만 평점
        verbose_name = "사용자 영화 선호도"
        verbose_name_plural = "사용자 영화 선호도들"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.rating}점"

    @property
    def rating_stars(self):
        """별점 문자열 반환"""
        return "★" * self.rating + "☆" * (5 - self.rating)

    def get_personality_contribution(self):
        """이 평점이 성격 분석에 기여하는 정도 계산"""
        # 평점에 따른 가중치
        weight = {1: 0.2, 2: 0.4, 3: 0.7, 4: 1.0, 5: 1.2}[self.rating]

        # 영화의 성격 특성과 가중치 결합
        movie_personality = self.movie.calculate_personality_scores()
        weighted_personality = {}

        for trait, score in movie_personality.items():
            weighted_personality[trait] = score * weight

        return weighted_personality


# Django Admin을 위한 Custom Manager (선택사항)
class MovieQuerySet(models.QuerySet):
    def with_high_rating(self, min_rating=7.0):
        return self.filter(vote_average__gte=min_rating)

    def by_genre(self, genre_name):
        return self.filter(genres__name__icontains=genre_name)

    def popular(self):
        return self.filter(popularity__gte=10.0)

    def recent(self):
        from datetime import datetime
        current_year = datetime.now().year
        return self.filter(release_date__year__gte=current_year - 2)


class MovieManager(models.Manager):
    def get_queryset(self):
        return MovieQuerySet(self.model, using=self._db)

    def with_high_rating(self, min_rating=7.0):
        return self.get_queryset().with_high_rating(min_rating)

    def by_genre(self, genre_name):
        return self.get_queryset().by_genre(genre_name)

    def popular(self):
        return self.get_queryset().popular()

    def recent(self):
        return self.get_queryset().recent()


# Movie 모델에 Custom Manager 추가
Movie.add_to_class('objects', MovieManager())
