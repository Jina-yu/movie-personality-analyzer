# analysis/services.py

import numpy as np
from collections import Counter, defaultdict
from django.contrib.auth.models import User
from movies.models import UserMoviePreference, Movie, Genre


class PersonalityAnalyzer:
    """
    검색 결과 [6] 패턴: 기능별 앱 분리 - 분석 전용 서비스
    movies 앱의 데이터를 사용하여 성격 분석 수행
    """

    def __init__(self):
        # 장르별 성격 특성 매핑
        self.genre_personality_mapping = {
            # 개방성 (새로운 경험, 창의성)
            'SF': {'openness': 0.9, 'conscientiousness': 0.2},
            '판타지': {'openness': 0.8, 'agreeableness': 0.3},
            '애니메이션': {'openness': 0.7, 'agreeableness': 0.6},

            # 외향성 (사교성, 에너지)
            '액션': {'extraversion': 0.8, 'neuroticism': -0.2},
            '코미디': {'extraversion': 0.9, 'agreeableness': 0.7},
            '모험': {'extraversion': 0.7, 'openness': 0.5},

            # 친화성 (협조, 공감)
            '로맨스': {'agreeableness': 0.8, 'neuroticism': 0.2},
            '가족': {'agreeableness': 0.9, 'conscientiousness': 0.6},
            '드라마': {'agreeableness': 0.6, 'openness': 0.4},

            # 성실성 (조직성, 책임감)
            '역사': {'conscientiousness': 0.8, 'openness': 0.5},
            '전쟁': {'conscientiousness': 0.7, 'neuroticism': 0.3},

            # 신경성 (감정적 불안정성)
            '공포': {'neuroticism': 0.8, 'openness': 0.2},
            '스릴러': {'neuroticism': 0.6, 'openness': 0.4},
            '미스터리': {'neuroticism': 0.5, 'openness': 0.6},
            '범죄': {'neuroticism': 0.4, 'conscientiousness': 0.4}
        }

    def analyze_user_personality(self, user: User) -> dict:
        """사용자의 영화 평가를 바탕으로 성격 분석"""
        try:
            print(f"🧠 analysis 앱에서 성격 분석: {user.username}")

            # movies 앱의 데이터 사용
            preferences = UserMoviePreference.objects.filter(
                user=user
            ).select_related('movie').prefetch_related('movie__genres')

            if preferences.count() < 5:
                raise ValueError("분석을 위해 최소 5편의 영화가 필요합니다.")

            # 데이터 수집 및 분석
            genre_data = self._collect_genre_data(preferences)
            personality_scores = self._calculate_personality_scores(genre_data)
            confidence = self._calculate_confidence(preferences.count(), len(genre_data))
            insights = self._generate_insights(personality_scores, genre_data, preferences.count())

            return {
                'personality': personality_scores,
                'confidence': confidence,
                'movies_analyzed': preferences.count(),
                'genre_analysis': {
                    'preferred_genres': dict(sorted(
                        {genre: data['count'] for genre, data in genre_data.items()}.items(),
                        key=lambda x: x[1], reverse=True
                    )[:5]),
                    'genre_ratings': {
                        genre: {
                            'average_rating': round(data['avg_rating'], 1),
                            'count': data['count'],
                            'preference_strength': round(data['weighted_score'], 2)
                        } for genre, data in genre_data.items()
                    }
                },
                'insights': insights
            }

        except Exception as e:
            print(f"❌ 성격 분석 실패: {e}")
            raise

    def _collect_genre_data(self, preferences):
        """장르별 데이터 수집"""
        genre_data = defaultdict(lambda: {
            'ratings': [],
            'count': 0,
            'total_score': 0
        })

        for pref in preferences:
            rating = pref.rating
            movie_genres = [genre.name for genre in pref.movie.genres.all()]

            for genre in movie_genres:
                genre_data[genre]['ratings'].append(rating)
                genre_data[genre]['count'] += 1
                genre_data[genre]['total_score'] += rating

        # 평균 계산
        for genre in genre_data:
            data = genre_data[genre]
            data['avg_rating'] = data['total_score'] / data['count']
            data['weighted_score'] = data['avg_rating'] * data['count'] / 5

        return dict(genre_data)

    def _calculate_personality_scores(self, genre_data):
        """Big Five 성격 점수 계산"""
        scores = {
            'openness': 50,
            'conscientiousness': 50,
            'extraversion': 50,
            'agreeableness': 50,
            'neuroticism': 50
        }

        for genre, data in genre_data.items():
            if genre in self.genre_personality_mapping:
                influence = data['weighted_score']
                mapping = self.genre_personality_mapping[genre]

                for trait, coefficient in mapping.items():
                    if trait in scores:
                        adjustment = coefficient * influence * 20
                        scores[trait] += adjustment

        # 정규화
        for trait in scores:
            scores[trait] = max(0, min(100, round(scores[trait], 1)))

        return scores

    def _calculate_confidence(self, movie_count, genre_count):
        """분석 신뢰도 계산"""
        movie_factor = min(movie_count / 15, 1.0)
        genre_factor = min(genre_count / 10, 1.0)
        confidence = (movie_factor * 0.6 + genre_factor * 0.4)
        return round(confidence, 3)

    def _generate_insights(self, scores, genre_data, movie_count):
        """개인화된 인사이트 생성"""
        insights = []

        # 가장 강한 특성
        strongest_trait = max(scores.items(), key=lambda x: x[1])
        if strongest_trait[1] > 65:
            trait_names = {
                'openness': '개방성',
                'conscientiousness': '성실성',
                'extraversion': '외향성',
                'agreeableness': '친화성',
                'neuroticism': '신경성'
            }

            insights.append({
                'type': 'strength',
                'title': f"당신의 강한 특성: {trait_names.get(strongest_trait[0])}",
                'description': f"이 특성에서 {strongest_trait[1]:.1f}점으로 높은 점수를 보입니다",
                'score': strongest_trait[1],
                'icon': '🌟'
            })

        # 최선호 장르
        if genre_data:
            top_genre = max(genre_data.items(), key=lambda x: x[1]['weighted_score'])
            insights.append({
                'type': 'preference',
                'title': f"최애 장르: {top_genre[0]}",
                'description': f"{top_genre[0]} 장르를 {top_genre[1]['count']}편 감상하며 평균 {top_genre[1]['avg_rating']:.1f}점을 주었습니다",
                'count': top_genre[1]['count'],
                'rating': top_genre[1]['avg_rating'],
                'icon': '🎭'
            })

        return insights


# 서비스 인스턴스
personality_analyzer = PersonalityAnalyzer()
