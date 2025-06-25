from rest_framework import serializers
from .models import Movie, UserMoviePreference


class MovieSerializer(serializers.ModelSerializer):
    """영화 데이터를 JSON으로 변환"""

    # 추가 필드들 (데이터베이스에는 없지만 API에서 제공하고 싶은 데이터)
    poster_url = serializers.ReadOnlyField()  # models.py의 @property 메서드 사용
    primary_category = serializers.SerializerMethodField()  # 커스텀 메서드로 계산

    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'original_title', 'overview',
            'release_date', 'genres', 'poster_path', 'poster_url',
            'vote_average', 'popularity', 'primary_category',
            'melodrama_score', 'comic_score', 'violent_score',
            'imaginative_score', 'exciting_score'
        ]
        read_only_fields = ['id', 'tmdb_id', 'created_at', 'updated_at']

    def get_primary_category(self, obj):
        """영화의 주요 카테고리를 계산해서 반환"""
        scores = {
            'melodrama': obj.melodrama_score,
            'comic': obj.comic_score,
            'violent': obj.violent_score,
            'imaginative': obj.imaginative_score,
            'exciting': obj.exciting_score
        }
        return max(scores, key=scores.get)


class UserMoviePreferenceSerializer(serializers.ModelSerializer):
    """사용자 영화 선호도를 JSON으로 변환"""

    # 관련 데이터도 함께 포함 (nested serialization)
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)  # 생성시에만 사용
    user = serializers.StringRelatedField(read_only=True)  # 사용자명만 표시

    class Meta:
        model = UserMoviePreference
        fields = ['id', 'user', 'movie', 'movie_id', 'rating', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_rating(self, value):
        """평점 유효성 검사"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("평점은 1-5 사이의 값이어야 합니다.")
        return value