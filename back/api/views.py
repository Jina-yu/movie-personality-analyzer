from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from movies.models import Movie, UserMoviePreference
from movies.serializers import MovieSerializer, UserMoviePreferenceSerializer
from movies.services import TMDBService
from movies.utils import MovieManager


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """영화 데이터 조회용 뷰셋"""
    # ... 기존 MovieViewSet 코드는 그대로 유지 ...
    queryset = Movie.objects.all().order_by('-popularity')
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'original_title', 'overview']
    filterset_fields = ['release_date', 'vote_average']

    @action(detail=False, methods=['get'])
    def popular(self, request):
        popular_movies = self.queryset.filter(popularity__gt=50)[:10]
        serializer = self.get_serializer(popular_movies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category', 'popular')

        if category == 'melodrama':
            movies = self.queryset.filter(melodrama_score__gt=0.5)[:10]
        elif category == 'comic':
            movies = self.queryset.filter(comic_score__gt=0.5)[:10]
        elif category == 'violent':
            movies = self.queryset.filter(violent_score__gt=0.5)[:10]
        elif category == 'imaginative':
            movies = self.queryset.filter(imaginative_score__gt=0.5)[:10]
        elif category == 'exciting':
            movies = self.queryset.filter(exciting_score__gt=0.5)[:10]
        else:
            movies = self.queryset[:10]

        serializer = self.get_serializer(movies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def search_and_save(self, request):
        query = request.data.get('query', '')

        if not query:
            return Response(
                {'error': '검색어를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            movie_manager = MovieManager()
            saved_movies = movie_manager.search_and_save_movie(query)

            serializer = self.get_serializer(saved_movies, many=True)
            return Response({
                'message': f'{len(saved_movies)}개의 영화를 저장했습니다.',
                'movies': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': f'검색 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserMoviePreferenceViewSet(viewsets.ModelViewSet):
    """사용자 영화 선호도 CRUD 뷰셋 - 중복 처리 개선"""

    queryset = UserMoviePreference.objects.all()
    serializer_class = UserMoviePreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """현재 사용자의 선호도만 반환"""
        return UserMoviePreference.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """POST 요청 처리 - update_or_create 사용"""
        movie_id = request.data.get('movie_id')
        rating = request.data.get('rating')

        if not movie_id or not rating:
            return Response({
                'error': 'movie_id와 rating이 필요합니다.',
                'example': '{"movie_id": 1, "rating": 5}'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 영화 객체 존재 확인
            movie = Movie.objects.get(id=movie_id)

            # update_or_create 사용 - Django의 강력한 기능!
            preference, created = UserMoviePreference.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating}
            )

            serializer = self.get_serializer(preference)

            if created:
                return Response({
                    'success': True,
                    'message': '새로운 평점이 생성되었습니다.',
                    'action': 'created',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': True,
                    'message': f'기존 평점이 {preference.rating}점으로 업데이트되었습니다.',
                    'action': 'updated',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

        except Movie.DoesNotExist:
            return Response({
                'error': f'movie_id {movie_id}에 해당하는 영화가 없습니다.',
                'suggestion': '/api/movies/ 에서 영화 목록을 확인해주세요.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': '처리 중 오류가 발생했습니다.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)