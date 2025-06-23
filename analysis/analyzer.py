from typing import List, Dict, Tuple
from movies.models import UserMoviePreference
from .models import PersonalityAnalysis, ValueAnalysis
import numpy as np
from collections import defaultdict


class PersonalityAnalyzer:
    """영화 선호도 기반 성격 분석기"""

    def __init__(self):
        # 연구 기반 상관계수 (영화 카테고리 → 성격 특성)
        self.correlation_matrix = {
            'melodrama': {
                'neuroticism': 0.09,  # 드라마 선호 → 감정적 민감성
                'agreeableness': 0.15,  # 로맨스 선호 → 협조성
                'openness': 0.05,  # 예술적 영화 → 개방성
                'extraversion': -0.02,  # 내향적 취향
                'conscientiousness': 0.03
            },
            'comic': {
                'extraversion': 0.12,  # 코미디 선호 → 사교성
                'agreeableness': 0.08,  # 가벼운 즐거움 → 친화성
                'openness': 0.04,  # 창의적 유머 감각
                'conscientiousness': -0.06,  # 계획보다 즉흥성
                'neuroticism': -0.08  # 긍정적 정서
            },
            'violent': {
                'extraversion': 0.07,  # 액션 선호 → 활동성
                'conscientiousness': 0.04,  # 목표 지향적
                'neuroticism': -0.05,  # 스트레스 저항력
                'openness': 0.02,
                'agreeableness': -0.03  # 경쟁적 성향
            },
            'imaginative': {
                'openness': 0.18,  # SF/판타지 → 창의성 (가장 강한 상관관계)
                'extraversion': 0.06,  # 모험 추구
                'conscientiousness': 0.02,
                'agreeableness': 0.01,
                'neuroticism': -0.01
            },
            'exciting': {
                'openness': 0.11,  # 스릴러/공포 → 새로운 경험
                'neuroticism': 0.07,  # 감정적 자극 추구
                'extraversion': 0.05,  # 자극적인 활동 선호
                'conscientiousness': -0.02,
                'agreeableness': -0.01
            }
        }

        # 가치관 매핑 (성격 특성 → 가치관)
        self.values_mapping = {
            'creativity_innovation': {
                'openness': 0.8,  # 개방성이 창의성과 강한 연관
                'extraversion': 0.3,
                'conscientiousness': 0.2
            },
            'social_connection': {
                'extraversion': 0.7,  # 외향성이 사회적 연결과 강한 연관
                'agreeableness': 0.6,
                'neuroticism': -0.3  # 불안감은 사회적 연결 방해
            },
            'achievement_success': {
                'conscientiousness': 0.8,  # 성실성이 성취와 강한 연관
                'extraversion': 0.4,
                'neuroticism': -0.2
            },
            'harmony_stability': {
                'agreeableness': 0.7,  # 친화성이 조화와 강한 연관
                'conscientiousness': 0.5,
                'neuroticism': -0.4  # 불안감은 안정성 방해
            },
            'authenticity_depth': {
                'openness': 0.6,  # 개방성이 진정성과 연관
                'neuroticism': 0.3,  # 내적 성찰과 연관
                'conscientiousness': 0.2
            }
        }

    def analyze_user_personality(self, user) -> Tuple[PersonalityAnalysis, ValueAnalysis]:
        """사용자의 영화 선호도를 분석하여 성격 특성 도출"""

        # 1. 사용자의 영화 선호도 데이터 수집
        preferences = UserMoviePreference.objects.filter(user=user).select_related('movie')

        if preferences.count() < 5:
            raise ValueError("성격 분석을 위해서는 최소 5편의 영화 평가가 필요합니다.")

        # 2. 카테고리별 선호도 점수 계산
        category_scores = self._calculate_category_preferences(preferences)

        # 3. 성격 특성 점수 계산
        personality_scores = self._calculate_personality_scores(category_scores)

        # 4. 신뢰도 점수 계산
        confidence = self._calculate_confidence(preferences.count(), category_scores)

        # 5. 가치관 점수 계산
        value_scores = self._calculate_value_scores(personality_scores)

        # 6. 결과 저장
        personality_analysis = self._save_personality_analysis(
            user, personality_scores, preferences.count(), confidence
        )
        value_analysis = self._save_value_analysis(personality_analysis, value_scores)

        return personality_analysis, value_analysis

    def _calculate_category_preferences(self, preferences) -> Dict[str, float]:
        """영화 선호도로부터 카테고리별 선호 점수 계산"""
        category_weighted_scores = defaultdict(float)
        category_total_weights = defaultdict(float)

        for pref in preferences:
            movie = pref.movie
            user_rating = pref.rating / 5.0  # 1-5 → 0.0-1.0 정규화

            # 각 카테고리별 가중 점수 계산
            categories = {
                'melodrama': movie.melodrama_score,
                'comic': movie.comic_score,
                'violent': movie.violent_score,
                'imaginative': movie.imaginative_score,
                'exciting': movie.exciting_score
            }

            for category, movie_category_score in categories.items():
                if movie_category_score > 0:  # 해당 카테고리에 속하는 영화만
                    weight = movie_category_score
                    weighted_score = user_rating * weight

                    category_weighted_scores[category] += weighted_score
                    category_total_weights[category] += weight

        # 가중 평균 계산
        category_preferences = {}
        for category in category_weighted_scores:
            if category_total_weights[category] > 0:
                category_preferences[category] = (
                        category_weighted_scores[category] / category_total_weights[category]
                )
            else:
                category_preferences[category] = 0.5  # 기본값

        return category_preferences

    def _calculate_personality_scores(self, category_scores: Dict[str, float]) -> Dict[str, float]:
        """카테고리 선호도로부터 성격 특성 점수 계산"""
        personality_scores = {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5
        }

        # 각 카테고리의 기여도를 성격 특성에 반영
        for category, preference_score in category_scores.items():
            if category in self.correlation_matrix:
                correlations = self.correlation_matrix[category]

                for trait, correlation in correlations.items():
                    # 선호도가 높을수록 해당 특성에 더 많은 영향
                    contribution = (preference_score - 0.5) * correlation
                    personality_scores[trait] += contribution

        # 0.0 ~ 1.0 범위로 정규화
        for trait in personality_scores:
            personality_scores[trait] = max(0.0, min(1.0, personality_scores[trait]))

        return personality_scores

    def _calculate_confidence(self, movie_count: int, category_scores: Dict[str, float]) -> float:
        """분석 신뢰도 계산"""
        # 영화 수에 따른 기본 신뢰도
        count_confidence = min(movie_count / 20.0, 1.0)  # 20편 이상이면 최대 신뢰도

        # 카테고리 분포 다양성 (한 카테고리에만 치우치지 않았는지)
        diversity = 1.0 - np.std(list(category_scores.values()))
        diversity_confidence = max(0.0, min(1.0, diversity))

        # 종합 신뢰도
        total_confidence = (count_confidence * 0.7) + (diversity_confidence * 0.3)
        return max(0.1, min(1.0, total_confidence))  # 최소 0.1, 최대 1.0

    def _calculate_value_scores(self, personality_scores: Dict[str, float]) -> Dict[str, float]:
        """성격 특성으로부터 가치관 점수 계산"""
        value_scores = {}

        for value, trait_weights in self.values_mapping.items():
            score = 0.0
            total_weight = 0.0

            for trait, weight in trait_weights.items():
                if trait in personality_scores:
                    if weight > 0:
                        score += personality_scores[trait] * weight
                    else:  # 음의 가중치 (반대 관계)
                        score += (1.0 - personality_scores[trait]) * abs(weight)
                    total_weight += abs(weight)

            if total_weight > 0:
                value_scores[value] = score / total_weight
            else:
                value_scores[value] = 0.5

        return value_scores

    def _save_personality_analysis(self, user, personality_scores, movie_count, confidence):
        """성격 분석 결과 저장"""
        # 기존 분석이 있으면 업데이트, 없으면 생성
        analysis, created = PersonalityAnalysis.objects.update_or_create(
            user=user,
            defaults={
                'openness': personality_scores['openness'],
                'conscientiousness': personality_scores['conscientiousness'],
                'extraversion': personality_scores['extraversion'],
                'agreeableness': personality_scores['agreeableness'],
                'neuroticism': personality_scores['neuroticism'],
                'movies_analyzed': movie_count,
                'confidence_score': confidence
            }
        )
        return analysis

    def _save_value_analysis(self, personality_analysis, value_scores):
        """가치관 분석 결과 저장"""
        value_analysis, created = ValueAnalysis.objects.update_or_create(
            personality_analysis=personality_analysis,
            defaults={
                'creativity_innovation': value_scores['creativity_innovation'],
                'social_connection': value_scores['social_connection'],
                'achievement_success': value_scores['achievement_success'],
                'harmony_stability': value_scores['harmony_stability'],
                'authenticity_depth': value_scores['authenticity_depth']
            }
        )
        return value_analysis
