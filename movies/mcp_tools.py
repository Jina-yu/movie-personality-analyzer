# movies/mcp_tools.py - 파일명 충돌 해결됨!

# 검색 결과 [5] 패턴: omarbenhamid 정확한 import
from mcp_server import ModelQueryToolset, MCPToolset
from .models import Movie, UserMoviePreference, Genre
from django.contrib.auth.models import User
from django.db.models import Avg
import json


# 검색 결과 [5] 패턴: ModelQueryToolset으로 Django 모델 노출
class MovieQueryTool(ModelQueryToolset):
    """영화 정보 조회 도구"""
    model = Movie


class UserQueryTool(ModelQueryToolset):
    """사용자 정보 조회 도구 (제한적)"""
    model = User

    def get_queryset(self):
        """검색 결과 [5] 패턴: 보안상 필요한 필드만 노출"""
        return super().get_queryset().only('id', 'username')


class UserMoviePreferenceQueryTool(ModelQueryToolset):
    """사용자의 영화 선호도 조회 도구"""
    model = UserMoviePreference

    def get_queryset(self):
        """검색 결과 [5] 패턴: self.request로 queryset 필터링"""
        return super().get_queryset().select_related('movie', 'user').prefetch_related('movie__genres')


class GenreQueryTool(ModelQueryToolset):
    """영화 장르 조회 도구"""
    model = Genre


# 검색 결과 [5] 패턴: MCPToolset으로 커스텀 도구 생성
class MoviePersonalityTools(MCPToolset):
    """영화 성격 분석 전용 도구"""

    def get_user_movie_analysis(self, username: str) -> dict:
        """특정 사용자의 영화 평가 분석 데이터"""
        try:
            user = User.objects.get(username=username)
            preferences = UserMoviePreference.objects.filter(user=user).select_related('movie').prefetch_related(
                'movie__genres')

            if preferences.count() < 5:
                return {
                    'error': f'분석을 위해 최소 5편의 영화 평가가 필요합니다. 현재: {preferences.count()}편',
                    'current_count': preferences.count(),
                    'required_count': 5
                }

            # 장르별 선호도 계산
            genre_stats = {}
            for pref in preferences:
                for genre in pref.movie.genres.all():
                    if genre.name not in genre_stats:
                        genre_stats[genre.name] = {
                            'ratings': [],
                            'count': 0,
                            'movies': []
                        }
                    genre_stats[genre.name]['ratings'].append(pref.rating)
                    genre_stats[genre.name]['count'] += 1
                    genre_stats[genre.name]['movies'].append(pref.movie.title)

            # 평균 계산
            for genre in genre_stats:
                ratings = genre_stats[genre]['ratings']
                genre_stats[genre]['average_rating'] = round(sum(ratings) / len(ratings), 1)

            return {
                'username': username,
                'total_movies_rated': preferences.count(),
                'overall_average': round(preferences.aggregate(Avg('rating'))['rating__avg'] or 0, 1),
                'genre_preferences': genre_stats,
                'recent_movies': [
                    {
                        'title': pref.movie.title,
                        'rating': pref.rating,
                        'genres': [g.name for g in pref.movie.genres.all()],
                        'release_year': pref.movie.release_date.year if pref.movie.release_date else None
                    }
                    for pref in preferences.order_by('-created_at')[:10]
                ],
                'analysis_ready': True
            }

        except User.DoesNotExist:
            return {'error': f'사용자 {username}을 찾을 수 없습니다.'}

    def calculate_personality_scores(self, username: str) -> dict:
        """Big Five 성격 점수 계산"""
        analysis_data = self.get_user_movie_analysis(username)

        if 'error' in analysis_data:
            return analysis_data

        genre_prefs = analysis_data['genre_preferences']

        # Big Five 성격 점수 계산
        personality_scores = {
            'openness': 50.0,
            'extraversion': 50.0,
            'agreeableness': 50.0,
            'conscientiousness': 50.0,
            'neuroticism': 50.0
        }

        # 개방성 계산 (SF, 판타지, 다큐멘터리 선호)
        if 'SF' in genre_prefs:
            sf_score = genre_prefs['SF']['average_rating']
            personality_scores['openness'] += (sf_score - 3) * 8

        if '판타지' in genre_prefs:
            fantasy_score = genre_prefs['판타지']['average_rating']
            personality_scores['openness'] += (fantasy_score - 3) * 6

        # 외향성 계산 (액션, 코미디 선호)
        if '액션' in genre_prefs:
            action_score = genre_prefs['액션']['average_rating']
            personality_scores['extraversion'] += (action_score - 3) * 7

        if '코미디' in genre_prefs:
            comedy_score = genre_prefs['코미디']['average_rating']
            personality_scores['extraversion'] += (comedy_score - 3) * 8

        # 친화성 계산 (로맨스, 드라마, 가족 선호)
        if '로맨스' in genre_prefs:
            romance_score = genre_prefs['로맨스']['average_rating']
            personality_scores['agreeableness'] += (romance_score - 3) * 8

        if '드라마' in genre_prefs:
            drama_score = genre_prefs['드라마']['average_rating']
            personality_scores['agreeableness'] += (drama_score - 3) * 5

        # 성실성 계산 (역사, 다큐멘터리 선호)
        if '역사' in genre_prefs:
            history_score = genre_prefs['역사']['average_rating']
            personality_scores['conscientiousness'] += (history_score - 3) * 7

        if '다큐멘터리' in genre_prefs:
            doc_score = genre_prefs['다큐멘터리']['average_rating']
            personality_scores['conscientiousness'] += (doc_score - 3) * 6

        # 신경성 계산 (공포, 스릴러 선호)
        if '공포' in genre_prefs:
            horror_score = genre_prefs['공포']['average_rating']
            personality_scores['neuroticism'] += (horror_score - 3) * 6

        if '스릴러' in genre_prefs:
            thriller_score = genre_prefs['스릴러']['average_rating']
            personality_scores['neuroticism'] += (thriller_score - 3) * 4

        # 점수 정규화 (0-100 범위)
        for trait in personality_scores:
            personality_scores[trait] = max(0, min(100, round(personality_scores[trait], 1)))

        return {
            'username': username,
            'personality_scores': personality_scores,
            'confidence': min(analysis_data['total_movies_rated'] / 15, 1.0),
            'movies_analyzed': analysis_data['total_movies_rated']
        }

    def generate_personality_report(self, username: str) -> str:
        """Claude가 읽기 쉬운 성격 분석 보고서 생성"""
        analysis = self.get_user_movie_analysis(username)
        scores = self.calculate_personality_scores(username)

        if 'error' in analysis or 'error' in scores:
            return f"분석 오류: {analysis.get('error', scores.get('error'))}"

        report = f"""
🎬 {username} 사용자 영화 성격 분석 보고서

📊 기본 정보:
- 총 평가 영화: {analysis['total_movies_rated']}편
- 전체 평균 평점: {analysis['overall_average']}점
- 분석 신뢰도: {scores['confidence']:.1%}

🎭 장르별 선호도 (평균 평점):
"""

        for genre, stats in sorted(analysis['genre_preferences'].items(),
                                   key=lambda x: x[1]['average_rating'], reverse=True):
            report += f"- {genre}: {stats['average_rating']}점 ({stats['count']}편)\n"

        report += f"""

🧠 Big Five 성격 특성 점수:
- 개방성: {scores['personality_scores']['openness']}점
- 외향성: {scores['personality_scores']['extraversion']}점
- 친화성: {scores['personality_scores']['agreeableness']}점
- 성실성: {scores['personality_scores']['conscientiousness']}점
- 신경성: {scores['personality_scores']['neuroticism']}점

🎬 최근 평가한 영화:
"""

        for movie in analysis['recent_movies'][:5]:
            report += f"- {movie['title']} ({movie['rating']}점) - {', '.join(movie['genres'])}\n"

        return report

    # 검색 결과 [5] 패턴: 이메일 도구 예시
    def send_analysis_email(self, to_email: str, username: str):
        """성격 분석 결과를 이메일로 전송"""
        from django.core.mail import send_mail

        report = self.generate_personality_report(username)

        try:
            send_mail(
                subject=f'{username}님의 영화 성격 분석 결과',
                message=report,
                from_email='noreply@movie-personality.com',
                recipient_list=[to_email],
                fail_silently=False,
            )
            return {'success': True, 'message': f'{to_email}로 분석 결과를 전송했습니다.'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
