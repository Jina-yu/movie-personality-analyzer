from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Movie(models.Model):
    """영화 정보를 저장하는 모델"""

    # TMDB에서 가져온 기본 정보
    tmdb_id = models.IntegerField(unique=True, verbose_name="TMDB ID")
    title = models.CharField(max_length=255, verbose_name="영화 제목")
    original_title = models.CharField(max_length=255, verbose_name="원제")
    overview = models.TextField(blank=True, verbose_name="줄거리")
    release_date = models.DateField(null=True, blank=True, verbose_name="개봉일")

    # 장르 정보 (JSON 형태로 저장)
    genres = models.JSONField(default=list, verbose_name="장르 목록")

    # MOVIE 모델 카테고리 점수
    melodrama_score = models.FloatField(default=0.0, verbose_name="멜로드라마 점수")
    comic_score = models.FloatField(default=0.0, verbose_name="코미디 점수")
    violent_score = models.FloatField(default=0.0, verbose_name="액션/폭력 점수")
    imaginative_score = models.FloatField(default=0.0, verbose_name="상상력 점수")
    exciting_score = models.FloatField(default=0.0, verbose_name="스릴러 점수")

    # 메타 정보
    poster_path = models.CharField(max_length=255, blank=True, verbose_name="포스터 경로")
    vote_average = models.FloatField(default=0.0, verbose_name="평점")
    popularity = models.FloatField(default=0.0, verbose_name="인기도")

    # 시스템 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "영화"
        verbose_name_plural = "영화들"
        ordering = ['-popularity']

    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'Unknown'})"

    @property
    def poster_url(self):
        """포스터 이미지 전체 URL 반환"""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None


class UserMoviePreference(models.Model):
    """사용자의 영화 선호도를 저장하는 모델"""

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="사용자")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="영화")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="평점 (1-5)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="평가일")

    class Meta:
        unique_together = ['user', 'movie']  # 한 사용자는 같은 영화에 한 번만 평점
        verbose_name = "사용자 영화 선호도"
        verbose_name_plural = "사용자 영화 선호도들"

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.rating}점"