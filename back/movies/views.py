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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_movie_preference(request):
    """영화 평점 추가/수정 API - 검색 결과 [1] 패턴 적용"""
    try:
        movie_id = request.data.get('movie_id')
        rating = request.data.get('rating')

        print(f"⭐ 평점 저장/수정 요청: 사용자 {request.user}, 영화 ID {movie_id}, 평점 {rating}")

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

        # 영화 존재 확인
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({
                'success': False,
                'error': '존재하지 않는 영화입니다.'
            }, status=404)

        # 검색 결과 [1] 패턴: update_or_create로 중복 방지
        preference, created = UserMoviePreference.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={'rating': rating}
        )

        action = "저장" if created else "수정"
        print(f"✅ 평점 {action} 완료: {movie.title} - {rating}점")

        return Response({
            'success': True,
            'message': f'"{movie.title}" 평점이 {action}되었습니다.',
            'created': created,
            'preference': {
                'id': preference.id,
                'movie_id': preference.movie.id,
                'movie_title': preference.movie.title,
                'rating': preference.rating,
                'action': action
            }
        })

    except Exception as e:
        print(f"❌ 평점 저장/수정 오류: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'평점 처리 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_movies_tmdb(request):
    """TMDB API를 사용한 영화 검색 - 장르 정보 포함"""
    query = request.GET.get('search', '')

    if not query:
        return Response({
            'success': False,
            'error': '검색어가 필요합니다.',
            'results': []
        })

    try:
        print(f"🔍 Django 뷰에서 영화 검색: '{query}'")

        # ✅ 장르 목록을 먼저 가져와서 캐시 (검색 결과 [6] 패턴)
        genres = tmdb_service.get_genres()
        genre_map = {g['id']: g['name'] for g in genres}
        print(f"📚 장르 맵 생성: {len(genre_map)}개 장르")

        # TMDB에서 영화 검색
        search_results = tmdb_service.search_movies_bilingual(query)

        if not search_results:
            return Response({
                'success': True,
                'results': [],
                'count': 0,
                'message': '검색 결과가 없습니다.'
            })

        movie_data = []
        for movie in search_results:
            # 🎭 검색 결과 [7] 패턴: genre_ids를 장르 이름으로 변환
            genre_names = []
            if movie.get('genre_ids'):
                genre_names = [genre_map.get(gid, f'장르ID:{gid}') for gid in movie['genre_ids']]
                print(f"🎬 {movie.get('title')} 장르 변환: {movie.get('genre_ids')} → {genre_names}")

            movie_data.append({
                'id': None,  # DB에 없으므로 None
                'tmdb_id': movie['id'],
                'title': movie.get('title', ''),
                'original_title': movie.get('original_title', ''),
                'overview': movie.get('overview', ''),
                'release_date': movie.get('release_date', ''),
                'vote_average': movie.get('vote_average', 0),
                'poster_url': f"{tmdb_service.image_base_url}{movie.get('poster_path', '')}" if movie.get(
                    'poster_path') else '',
                'backdrop_url': f"https://image.tmdb.org/t/p/w1280{movie.get('backdrop_path', '')}" if movie.get(
                    'backdrop_path') else '',
                'genres': genre_names,  # ✅ 변환된 장르 이름들
                'genre_names': genre_names,  # ✅ 호환성을 위한 추가
                'popularity': movie.get('popularity', 0),
                'source': 'tmdb_search'
            })

        print(f"✅ 검색 완료: {len(movie_data)}개 영화 (장르 정보 포함)")

        return Response({
            'success': True,
            'results': movie_data,
            'count': len(movie_data),
            'message': f'"{query}" 검색 결과'
        })

    except Exception as e:
        print(f"❌ 영화 검색 오류: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'검색 중 오류가 발생했습니다: {str(e)}',
            'results': []
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_tmdb_movie(request):
    """TMDB 영화를 DB에 저장하고 평점 추가 (검색 결과 [6] 패턴)"""
    try:
        tmdb_id = request.data.get('tmdb_id')
        rating = request.data.get('rating')

        print(f"💾 TMDB 영화 저장 요청: ID {tmdb_id}, 평점 {rating}")

        if not tmdb_id:
            return Response({
                'success': False,
                'error': 'tmdb_id가 필요합니다.'
            }, status=400)

        if rating and (rating not in [1, 2, 3, 4, 5]):
            return Response({
                'success': False,
                'error': 'rating은 1-5 사이의 값이어야 합니다.'
            }, status=400)

        # TMDB에서 영화 정보 가져와서 DB에 저장
        movie = tmdb_service.save_movie_from_tmdb(tmdb_id)
        if not movie:
            return Response({
                'success': False,
                'error': 'TMDB에서 영화 정보를 가져올 수 없습니다.'
            }, status=404)

        response_data = {
            'success': True,
            'message': f'"{movie.title}" 영화가 저장되었습니다.',
            'movie': {
                'id': movie.id,
                'tmdb_id': movie.tmdb_id,
                'title': movie.title,
                'genres': [genre.name for genre in movie.genres.all()],
                'poster_url': movie.poster_url,
                'release_date': movie.release_date
            }
        }

        # 평점도 함께 저장하는 경우
        if rating:
            try:
                preference, created = UserMoviePreference.objects.update_or_create(
                    user=request.user,
                    movie=movie,
                    defaults={'rating': rating}
                )
                response_data['rating_saved'] = True
                response_data['message'] += f' 평점 {rating}점도 저장되었습니다.'
            except Exception as rating_error:
                print(f"❌ 평점 저장 실패: {rating_error}")
                response_data['rating_saved'] = False
                response_data['rating_error'] = str(rating_error)

        print(f"✅ TMDB 영화 저장 완료: {movie.title}")
        return Response(response_data, status=201)

    except Exception as e:
        print(f"❌ TMDB 영화 저장 오류: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'영화 저장 중 오류가 발생했습니다: {str(e)}'
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


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def preferences_handler(request):
    """사용자 영화 선호도 처리 - GET, POST, DELETE 지원"""

    if request.method == 'GET':
        try:
            print(f"📨 preferences_handler GET 요청 - 사용자: {request.user}")

            # 🎭 장르 정보를 포함하여 선호도 조회
            preferences = UserMoviePreference.objects.filter(
                user=request.user
            ).select_related('movie').prefetch_related('movie__genres').order_by('-created_at')

            preference_data = []
            for pref in preferences:
                # 영화의 장르 정보 추출
                movie_genres = [genre.name for genre in pref.movie.genres.all()]

                movie_data = {
                    'id': pref.movie.id,
                    'tmdb_id': pref.movie.tmdb_id,
                    'title': pref.movie.title,
                    'original_title': pref.movie.original_title,
                    'overview': pref.movie.overview,
                    'release_date': str(pref.movie.release_date) if pref.movie.release_date else '',
                    'poster_path': pref.movie.poster_path,
                    'backdrop_path': pref.movie.backdrop_path,
                    'vote_average': pref.movie.vote_average,
                    'vote_count': pref.movie.vote_count,
                    'popularity': pref.movie.popularity,
                    'poster_url': pref.movie.poster_url,
                    'backdrop_url': pref.movie.backdrop_url,
                    'genres': movie_genres,  # ✅ 장르 정보 포함
                    'genre_names': movie_genres,  # ✅ 호환성을 위한 추가 필드
                }

                preference_data.append({
                    'id': pref.id,
                    'movie': movie_data,
                    'rating': pref.rating,
                    'created_at': pref.created_at.isoformat(),
                    'updated_at': pref.updated_at.isoformat()
                })

            print(f"✅ GET 선호도 응답: {len(preference_data)}개 (장르 정보 포함)")

            # 첫 번째 영화의 장르 정보 로깅 (수정된 부분)
            if preference_data:
                first_movie_genres = preference_data[0]['movie']['genres']
                print(f"📊 첫 번째 영화 장르: {first_movie_genres}")

            return Response({
                'success': True,
                'results': preference_data,
                'count': len(preference_data)
            })

        except Exception as e:
            print(f"❌ GET 선호도 오류: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'error': str(e),
                'results': []
            }, status=500)

    elif request.method == 'POST':
        try:
            print(f"📨 preferences_handler POST 요청 - 사용자: {request.user}")
            print(f"📝 POST 요청 데이터: {request.data}")

            movie_id = request.data.get('movie_id')
            rating = request.data.get('rating')

            if not movie_id or not rating:
                return Response({
                    'success': False,
                    'error': 'movie_id와 rating이 필요합니다.'
                }, status=400)

            # 평점 유효성 검사
            try:
                rating = int(rating)
                if rating not in [1, 2, 3, 4, 5]:
                    raise ValueError()
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'rating은 1-5 사이의 정수여야 합니다.'
                }, status=400)

            # 영화 존재 확인
            try:
                movie = Movie.objects.get(id=movie_id)
            except Movie.DoesNotExist:
                return Response({
                    'success': False,
                    'error': '존재하지 않는 영화입니다.'
                }, status=404)

            # 평점 저장/수정 (중복 방지)
            preference, created = UserMoviePreference.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating}
            )

            action = "저장" if created else "수정"
            print(f"✅ 평점 {action} 완료: {movie.title} - {rating}점")

            return Response({
                'success': True,
                'message': f'"{movie.title}" 평점이 {action}되었습니다.',
                'created': created,
                'preference': {
                    'id': preference.id,
                    'movie_id': preference.movie.id,
                    'movie_title': preference.movie.title,
                    'rating': preference.rating,
                    'action': action
                }
            })

        except Exception as e:
            print(f"❌ 평점 저장/수정 오류: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'error': f'평점 처리 중 오류가 발생했습니다: {str(e)}'
            }, status=500)

    elif request.method == 'DELETE':
        try:
            print(f"🗑️ preferences_handler DELETE 요청 - 사용자: {request.user}")
            print(f"📝 DELETE 요청 데이터: {request.data}")

            # DELETE 요청에서는 URL 파라미터나 request body에서 ID를 가져올 수 있음
            preference_id = request.data.get('preference_id') or request.data.get('id')
            movie_id = request.data.get('movie_id')

            preference = None

            # preference_id가 있으면 우선 사용
            if preference_id:
                preference = UserMoviePreference.objects.filter(
                    id=preference_id,
                    user=request.user
                ).first()
            # movie_id로 찾기
            elif movie_id:
                preference = UserMoviePreference.objects.filter(
                    movie_id=movie_id,
                    user=request.user
                ).first()

            if not preference:
                return Response({
                    'success': False,
                    'error': '삭제할 평점을 찾을 수 없습니다.'
                }, status=404)

            movie_title = preference.movie.title
            preference.delete()

            print(f"✅ 평점 삭제 완료: {movie_title}")

            return Response({
                'success': True,
                'message': f'"{movie_title}" 평점이 삭제되었습니다.',
                'movie_title': movie_title
            })

        except Exception as e:
            print(f"❌ 평점 삭제 오류: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'error': f'평점 삭제 중 오류가 발생했습니다: {str(e)}'
            }, status=500)

    else:
        return Response({
            'success': False,
            'error': f'허용되지 않은 메서드입니다: {request.method}'
        }, status=405)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_movie_preference(request, movie_id):
    """영화 평점 삭제 API - URL 파라미터 방식"""
    try:
        print(f"🗑️ 평점 삭제 요청 - 사용자: {request.user}, 영화 ID: {movie_id}")

        # 해당 사용자의 해당 영화 평점 찾기
        preference = UserMoviePreference.objects.filter(
            user=request.user,
            movie_id=movie_id
        ).first()

        if not preference:
            # TMDB ID로도 시도해보기
            preference = UserMoviePreference.objects.filter(
                user=request.user,
                movie__tmdb_id=movie_id
            ).first()

        if preference:
            movie_title = preference.movie.title
            preference.delete()
            print(f"✅ 평점 삭제 완료: {movie_title}")

            return Response({
                'success': True,
                'message': f'"{movie_title}" 평점이 삭제되었습니다.',
                'movie_title': movie_title
            })
        else:
            print(f"❌ 평점을 찾을 수 없음: 영화 ID {movie_id}")
            return Response({
                'success': False,
                'error': '해당 영화의 평점을 찾을 수 없습니다.'
            }, status=404)

    except Exception as e:
        print(f"❌ 평점 삭제 오류: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'평점 삭제 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_popular_movies(request):
    """TMDB 인기 영화 목록 조회 + 장르 정보 완벽 처리"""
    try:
        page = request.GET.get('page', 1)
        movie_type = request.GET.get('type', 'popular')

        print(f"🔥 인기 영화 요청: 타입={movie_type}, 페이지={page}")

        # ✅ 장르 목록을 한 번만 가져와서 캐시
        print("📚 장르 목록 로딩 중...")
        genres = tmdb_service.get_genres()
        genre_map = {g['id']: g['name'] for g in genres}
        print(f"📚 장르 맵 생성 완료: {len(genre_map)}개")

        # TMDB에서 인기 영화 가져오기
        if movie_type == 'top_rated':
            tmdb_movies = tmdb_service.get_top_rated_movies(page)
        else:
            tmdb_movies = tmdb_service.get_popular_movies(page)

        movie_data = []

        # 현재 사용자가 인증된 경우 평가 정보도 함께 가져오기
        user_ratings = {}
        if request.user.is_authenticated:
            user_preferences = UserMoviePreference.objects.filter(user=request.user)
            user_ratings = {pref.movie.tmdb_id: pref.rating for pref in user_preferences}
            print(f"👤 사용자 평점 로드: {len(user_ratings)}개")

        # TMDB 영화 데이터 변환 (장르 정보 완벽 처리)
        for tmdb_movie in tmdb_movies:
            # ✅ 캐시된 장르 맵 사용하여 변환
            genre_names = []
            if tmdb_movie.get('genre_ids'):
                genre_names = [genre_map.get(gid, f'장르ID:{gid}') for gid in tmdb_movie['genre_ids']]
                print(f"🎬 {tmdb_movie.get('title')} 장르: {genre_names}")

            # 사용자 평점 확인
            user_rating = user_ratings.get(tmdb_movie['id'], 0)
            is_evaluated = user_rating > 0

            movie_data.append({
                'id': None,
                'tmdb_id': tmdb_movie['id'],
                'title': tmdb_movie.get('title', ''),
                'overview': tmdb_movie.get('overview', ''),
                'release_date': tmdb_movie.get('release_date', ''),
                'vote_average': tmdb_movie.get('vote_average', 0),
                'poster_url': f"{tmdb_service.image_base_url}{tmdb_movie.get('poster_path', '')}" if tmdb_movie.get(
                    'poster_path') else '',
                'backdrop_url': f"https://image.tmdb.org/t/p/w1280{tmdb_movie.get('backdrop_path', '')}" if tmdb_movie.get(
                    'backdrop_path') else '',
                'genres': genre_names,  # ✅ 변환된 장르 정보
                'genre_names': genre_names,  # ✅ 호환성을 위한 추가
                'popularity': tmdb_movie.get('popularity', 0),
                'user_rating': user_rating,
                'is_evaluated': is_evaluated,
                'source': 'tmdb_popular'
            })

        # 평가된 영화 우선 정렬
        movie_data.sort(key=lambda x: (
            not x['is_evaluated'],
            -x['popularity']
        ))

        print(f"📊 정렬 결과: 평가됨 {len([m for m in movie_data if m['is_evaluated']])}개, "
              f"미평가 {len([m for m in movie_data if not m['is_evaluated']])}개")

        return Response({
            'success': True,
            'results': movie_data,
            'count': len(movie_data),
            'message': f'{movie_type} 영화 목록 (평가된 영화 우선)',
            'performance': {
                'genre_api_calls': 1,
                'total_movies': len(movie_data)
            }
        })

    except Exception as e:
        print(f"❌ 인기 영화 조회 오류: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': f'인기 영화 조회 실패: {str(e)}',
            'results': []
        }, status=500)