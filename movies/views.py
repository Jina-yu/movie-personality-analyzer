# movies/views.py (기존 내용에 추가)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Movie


@api_view(['GET'])
@permission_classes([AllowAny])  # 일단 인증 없이 테스트
def movie_list(request):
    """영화 목록 조회 API"""
    try:
        print(f"🎬 영화 목록 요청 - 사용자: {request.user}")

        # 검색 파라미터 처리
        search_query = request.GET.get('search', '')

        if search_query:
            movies = Movie.objects.filter(title__icontains=search_query)[:20]
        else:
            movies = Movie.objects.all()[:20]

        # 영화 데이터 직렬화
        movie_data = []
        for movie in movies:
            movie_data.append({
                'id': movie.id,
                'title': movie.title,
                'overview': movie.overview,
                'release_date': movie.release_date,
                'vote_average': movie.vote_average,
                'poster_url': movie.poster_url,
                'genres': [{'name': genre.name} for genre in movie.genres.all()] if hasattr(movie, 'genres') else []
            })

        response_data = {
            'success': True,
            'count': len(movie_data),
            'results': movie_data
        }

        print(f"✅ 영화 목록 응답: {len(movie_data)}개")
        return Response(response_data)

    except Exception as e:
        print(f"❌ 영화 목록 오류: {e}")
        return Response({
            'error': f'영화 목록 조회 실패: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_movies(request):
    """영화 검색 API"""
    try:
        search_query = request.GET.get('search', '')
        print(f"🔍 영화 검색: {search_query}")

        if not search_query:
            return Response({
                'error': '검색어를 입력해주세요.'
            }, status=400)

        movies = Movie.objects.filter(title__icontains=search_query)[:10]

        movie_data = []
        for movie in movies:
            movie_data.append({
                'id': movie.id,
                'title': movie.title,
                'overview': movie.overview,
                'release_date': movie.release_date,
                'vote_average': movie.vote_average,
                'poster_url': movie.poster_url,
            })

        return Response({
            'success': True,
            'results': movie_data,
            'count': len(movie_data)
        })

    except Exception as e:
        return Response({
            'error': f'검색 실패: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_and_save_movies(request):
    """영화 검색 후 저장 API"""
    try:
        query = request.data.get('query', '')
        print(f"🔍💾 영화 검색 후 저장: {query}")

        # 임시 응답 (실제 TMDB API 연동 로직으로 교체 필요)
        response_data = {
            'success': True,
            'message': f'"{query}" 검색 완료',
            'movies': []  # 실제 검색 결과로 교체
        }

        return Response(response_data)

    except Exception as e:
        return Response({
            'error': f'검색 저장 실패: {str(e)}'
        }, status=500)
