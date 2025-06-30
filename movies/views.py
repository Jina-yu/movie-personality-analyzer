from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .tmdb_service import tmdb_service, check_tmdb_connection
from .models import Movie, UserMoviePreference
import traceback
from django.conf import settings
import requests



@api_view(['GET'])
@permission_classes([AllowAny])  # 임시로 인증 제거
def movie_list(request):
    """영화 목록 조회 API"""
    try:
        print(f"🎬 영화 목록 요청 - 사용자: {request.user}")

        search_query = request.GET.get('search', '')
        print(f"🔍 검색어: '{search_query}'")

        if search_query:
            movies = Movie.objects.filter(title__icontains=search_query)[:20]
        else:
            movies = Movie.objects.all()[:20]

        print(f"📊 조회된 영화 수: {movies.count()}")

        movie_data = []
        for movie in movies:
            movie_data.append({
                'id': movie.id,
                'title': movie.title,
                'overview': getattr(movie, 'overview', ''),
                'release_date': str(getattr(movie, 'release_date', '')),
                'vote_average': getattr(movie, 'vote_average', 0),
                'poster_url': getattr(movie, 'poster_url', ''),
                'tmdb_id': getattr(movie, 'tmdb_id', 0),
            })

        response_data = {
            'success': True,
            'count': len(movie_data),
            'results': movie_data,
            'message': f"'{search_query}' 검색 결과" if search_query else "전체 영화 목록"
        }

        print(f"✅ 영화 목록 응답: {len(movie_data)}개")
        return Response(response_data)

    except Exception as e:
        print(f"❌ 영화 목록 오류: {e}")
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'영화 목록 조회 실패: {str(e)}',
            'count': 0,
            'results': []
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_movies_tmdb(request):
    """실제 TMDB API를 통한 영화 검색"""
    try:
        query = request.GET.get('search', '').strip()
        if not query:
            return Response({
                'success': False,
                'error': '검색어를 입력해주세요.',
                'results': []
            }, status=400)

        print(f"🔍 Django 뷰에서 영화 검색: '{query}'")

        # 1. 기존 DB에서 검색
        db_movies = Movie.objects.filter(title__icontains=query)[:5]
        movie_data = []

        # DB 영화들 추가
        for movie in db_movies:
            genres_list = [genre.name for genre in movie.genres.all()]
            movie_data.append({
                'id': movie.id,
                'tmdb_id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'release_date': str(movie.release_date) if movie.release_date else '',
                'vote_average': movie.vote_average,
                'poster_url': movie.poster_url,
                'backdrop_url': getattr(movie, 'backdrop_url', ''),
                'genres': genres_list,
                'source': 'db'
            })

        # 2. TMDB API 직접 호출 (Django shell에서 성공한 것과 동일한 코드)
        api_key = getattr(settings, 'TMDB_API_KEY', '')
        if api_key:
            print(f"📡 TMDB API 호출 중... (API 키: {len(api_key)} 문자)")

            url = "https://api.themoviedb.org/3/search/movie"
            params = {
                'api_key': api_key,
                'language': 'ko-KR',
                'query': query,
                'include_adult': False
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                print(f"📡 TMDB 응답 상태: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    tmdb_results = data.get('results', [])
                    print(f"✅ TMDB 검색 성공: {len(tmdb_results)}개")

                    # TMDB 결과를 movie_data에 추가
                    existing_tmdb_ids = {movie.tmdb_id for movie in db_movies}

                    for tmdb_movie in tmdb_results[:10]:  # 최대 10개
                        if tmdb_movie['id'] not in existing_tmdb_ids:
                            movie_data.append({
                                'id': None,
                                'tmdb_id': tmdb_movie['id'],
                                'title': tmdb_movie.get('title', ''),
                                'overview': tmdb_movie.get('overview', ''),
                                'release_date': tmdb_movie.get('release_date', ''),
                                'vote_average': tmdb_movie.get('vote_average', 0),
                                'poster_url': f"https://image.tmdb.org/t/p/w500{tmdb_movie.get('poster_path', '')}" if tmdb_movie.get(
                                    'poster_path') else '',
                                'backdrop_url': f"https://image.tmdb.org/t/p/w1280{tmdb_movie.get('backdrop_path', '')}" if tmdb_movie.get(
                                    'backdrop_path') else '',
                                'genres': [],  # 일단 비워둠 (genre_ids 변환 필요)
                                'source': 'tmdb'
                            })
                else:
                    print(f"❌ TMDB API 오류: {response.status_code} - {response.text[:100]}")

            except requests.RequestException as e:
                print(f"❌ TMDB 요청 실패: {e}")
        else:
            print("❌ TMDB API 키가 설정되지 않음")

        return Response({
            'success': True,
            'results': movie_data,
            'count': len(movie_data),
            'message': f"'{query}' 검색 완료 (총 {len(movie_data)}개)",
            'debug': {
                'db_results': len([m for m in movie_data if m['source'] == 'db']),
                'tmdb_results': len([m for m in movie_data if m['source'] == 'tmdb']),
                'api_key_configured': bool(api_key)
            }
        })

    except Exception as e:
        print(f"❌ search_movies_tmdb 오류: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'검색 실패: {str(e)}',
            'results': []
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_tmdb_movie(request):
    """TMDB 영화를 DB에 저장하고 평점 추가"""
    try:
        tmdb_id = request.data.get('tmdb_id')
        rating = request.data.get('rating')

        if not tmdb_id or not rating:
            return Response({
                'success': False,
                'error': 'tmdb_id와 rating이 필요합니다.'
            }, status=400)

        # TMDB에서 영화 상세 정보 가져와서 저장
        movie_details = tmdb_service.get_movie_details(tmdb_id)
        if not movie_details:
            return Response({
                'success': False,
                'error': '영화 정보를 가져올 수 없습니다.'
            }, status=404)

        # 영화 저장
        movie = tmdb_service.save_movie_from_tmdb(movie_details)
        if not movie:
            return Response({
                'success': False,
                'error': '영화 저장에 실패했습니다.'
            }, status=500)

        # 평점 저장
        preference, created = UserMoviePreference.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'rating': rating}
        )

        return Response({
            'success': True,
            'message': f'{movie.title} 평점이 저장되었습니다.',
            'movie': {
                'id': movie.id,
                'title': movie.title,
                'genres': [genre.name for genre in movie.genres.all()]
            }
        })

    except Exception as e:
        print(f"❌ TMDB 영화 저장 오류: {e}")
        return Response({
            'success': False,
            'error': f'저장 실패: {str(e)}'
        }, status=500)



# API 연결 상태 확인 엔드포인트
@api_view(['GET'])
@permission_classes([AllowAny])
def check_tmdb_status(request):
    """TMDB API 연결 상태 확인"""
    is_connected = check_tmdb_connection()
    return Response({
        'tmdb_connected': is_connected,
        'api_key_configured': bool(tmdb_service.api_key),
        'message': 'TMDB API 연결됨' if is_connected else 'TMDB API 연결 실패'
    })




@api_view(['POST'])
@permission_classes([AllowAny])
def search_and_save_movies(request):
    """영화 검색 후 저장 API"""
    try:
        query = request.data.get('query', '')
        print(f"🔍💾 영화 검색 후 저장: '{query}'")

        if not query:
            return Response({
                'success': False,
                'error': '검색어가 필요합니다.',
                'movies': []
            }, status=400)

        response_data = {
            'success': True,
            'message': f"'{query}' 검색 완료",
            'movies': [
                {
                    'id': 1,
                    'title': f'{query} 관련 영화 1',
                    'overview': '임시 영화 설명',
                    'poster_url': '',
                    'vote_average': 8.5
                }
            ]
        }

        return Response(response_data)

    except Exception as e:
        print(f"❌ 검색 저장 오류: {e}")
        return Response({
            'success': False,
            'error': f'검색 저장 실패: {str(e)}',
            'movies': []
        }, status=500)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def preferences_handler(request):
    """통합 preferences 처리 함수"""
    try:
        print(f"📨 preferences_handler 요청: {request.method} - 사용자: {request.user}")

        if request.method == 'GET':
            preferences = UserMoviePreference.objects.filter(
                user=request.user
            ).select_related('movie').order_by('-created_at')

            preference_data = []
            for pref in preferences:
                preference_data.append({
                    'id': pref.id,
                    'movie': {
                        'id': pref.movie.id,
                        'title': pref.movie.title,
                        'poster_url': getattr(pref.movie, 'poster_url', ''),
                        'vote_average': getattr(pref.movie, 'vote_average', 0),
                        'release_date': pref.movie.release_date,
                    },
                    'rating': pref.rating,
                    'created_at': pref.created_at.isoformat(),
                })

            response_data = {
                'success': True,
                'count': len(preference_data),
                'results': preference_data
            }

            print(f"✅ GET 선호도 응답: {len(preference_data)}개")
            return Response(response_data)

        elif request.method == 'POST':
            print(f"📝 POST 요청 데이터: {request.data}")

            movie_id = request.data.get('movie_id')
            rating = request.data.get('rating')

            if not movie_id or not rating:
                return Response({
                    'success': False,
                    'error': 'movie_id와 rating이 필요합니다.'
                }, status=400)

            try:
                rating = int(rating)
                if rating not in [1, 2, 3, 4, 5]:
                    raise ValueError()
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'rating은 1-5 사이의 정수여야 합니다.'
                }, status=400)

            try:
                movie = Movie.objects.get(id=movie_id)
                print(f"🎬 영화 확인: {movie.title}")
            except Movie.DoesNotExist:
                return Response({
                    'success': False,
                    'error': '존재하지 않는 영화입니다.'
                }, status=404)

            preference, created = UserMoviePreference.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating}
            )

            response_data = {
                'success': True,
                'message': '새 평점이 저장되었습니다.' if created else '평점이 업데이트되었습니다.',
                'preference': {
                    'id': preference.id,
                    'movie_id': preference.movie.id,
                    'movie_title': preference.movie.title,
                    'rating': preference.rating,
                    'created': created
                }
            }

            print(f"✅ POST 평점 저장 성공: {movie.title} - {rating}점")
            return Response(response_data, status=201 if created else 200)
        return None

    except Exception as e:
        print(f"❌ preferences_handler 오류: {e}")
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'요청 처리 실패: {str(e)}'
        }, status=500)
