from rest_framework import serializers
from .models import PersonalityAnalysis, ValueAnalysis
from movies.models import UserMoviePreference


class PersonalityAnalysisSerializer(serializers.ModelSerializer):
    """성격 분석 결과 직렬화기"""

    user = serializers.StringRelatedField(read_only=True)
    personality_summary = serializers.ReadOnlyField()

    # 성격 특성 설명 추가
    trait_descriptions = serializers.SerializerMethodField()

    class Meta:
        model = PersonalityAnalysis
        fields = [
            'id', 'user', 'openness', 'conscientiousness', 'extraversion',
            'agreeableness', 'neuroticism', 'movies_analyzed', 'confidence_score',
            'created_at', 'personality_summary', 'trait_descriptions'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def get_trait_descriptions(self, obj):
        """각 성격 특성에 대한 설명 반환"""

        def get_level_description(score):
            if score >= 0.7:
                return "높음"
            elif score >= 0.4:
                return "보통"
            else:
                return "낮음"

        return {
            'openness': {
                'score': obj.openness,
                'level': get_level_description(obj.openness),
                'description': self._get_openness_description(obj.openness)
            },
            'conscientiousness': {
                'score': obj.conscientiousness,
                'level': get_level_description(obj.conscientiousness),
                'description': self._get_conscientiousness_description(obj.conscientiousness)
            },
            'extraversion': {
                'score': obj.extraversion,
                'level': get_level_description(obj.extraversion),
                'description': self._get_extraversion_description(obj.extraversion)
            },
            'agreeableness': {
                'score': obj.agreeableness,
                'level': get_level_description(obj.agreeableness),
                'description': self._get_agreeableness_description(obj.agreeableness)
            },
            'neuroticism': {
                'score': obj.neuroticism,
                'level': get_level_description(obj.neuroticism),
                'description': self._get_neuroticism_description(obj.neuroticism)
            }
        }

    def _get_openness_description(self, score):
        if score >= 0.7:
            return "창의적이고 새로운 경험을 추구하는 성향이 매우 강합니다. 예술과 문화에 관심이 많고 상상력이 풍부합니다."
        elif score >= 0.4:
            return "새로운 것과 전통적인 것을 균형있게 수용합니다. 상황에 따라 창의적이기도 하고 현실적이기도 합니다."
        else:
            return "실용적이고 현실적인 접근을 선호하며 안정성을 중시합니다. 검증된 방법을 선호하는 편입니다."

    def _get_conscientiousness_description(self, score):
        if score >= 0.7:
            return "매우 책임감이 강하고 계획적입니다. 목표를 설정하고 체계적으로 달성하는 능력이 뛰어납니다."
        elif score >= 0.4:
            return "적당한 수준의 계획성을 가지고 있습니다. 상황에 따라 체계적이기도 하고 유연하기도 합니다."
        else:
            return "즉흥적이고 유연한 성향입니다. 계획보다는 그때그때 상황에 맞춰 행동하는 것을 선호합니다."

    def _get_extraversion_description(self, score):
        if score >= 0.7:
            return "매우 사교적이고 활동적입니다. 사람들과의 상호작용을 즐기고 에너지가 넘칩니다."
        elif score >= 0.4:
            return "상황에 따라 사교적이기도 하고 조용하기도 합니다. 필요에 따라 사람들과 어울리거나 혼자 시간을 즐깁니다."
        else:
            return "조용하고 사려깊은 성격입니다. 소수의 깊은 관계를 선호하고 혼자만의 시간을 소중히 여깁니다."

    def _get_agreeableness_description(self, score):
        if score >= 0.7:
            return "매우 협조적이고 신뢰할 수 있는 성격입니다. 다른 사람을 배려하고 갈등을 피하려고 노력합니다."
        elif score >= 0.4:
            return "적절한 수준의 협조성을 가지고 있습니다. 상황에 따라 협력적이기도 하고 경쟁적이기도 합니다."
        else:
            return "독립적이고 경쟁적인 성향입니다. 자신의 이익을 우선시하고 필요시 강하게 주장할 수 있습니다."

    def _get_neuroticism_description(self, score):
        if score >= 0.7:
            return "감정적으로 민감한 편입니다. 스트레스나 변화에 대해 강하게 반응할 수 있지만, 감정이 풍부하고 공감능력이 뛰어납니다."
        elif score >= 0.4:
            return "대체로 안정적인 정서를 유지합니다. 때때로 감정적이 될 수 있지만 금세 회복하는 편입니다."
        else:
            return "매우 안정적이고 침착한 성격입니다. 스트레스나 압박 상황에서도 냉정함을 유지할 수 있습니다."


class ValueAnalysisSerializer(serializers.ModelSerializer):
    """가치관 분석 결과 직렬화기"""

    top_values = serializers.ReadOnlyField()
    value_descriptions = serializers.SerializerMethodField()

    class Meta:
        model = ValueAnalysis
        fields = [
            'creativity_innovation', 'social_connection', 'achievement_success',
            'harmony_stability', 'authenticity_depth', 'top_values', 'value_descriptions'
        ]

    def get_value_descriptions(self, obj):
        """각 가치관에 대한 설명 반환"""
        return {
            'creativity_innovation': {
                'score': obj.creativity_innovation,
                'name': '창의성과 혁신',
                'description': '새로운 아이디어와 독창적인 해결책을 추구하는 성향'
            },
            'social_connection': {
                'score': obj.social_connection,
                'name': '사회적 연결',
                'description': '타인과의 관계와 소속감을 중시하는 성향'
            },
            'achievement_success': {
                'score': obj.achievement_success,
                'name': '성취와 성공',
                'description': '목표 달성과 성과를 중요하게 생각하는 성향'
            },
            'harmony_stability': {
                'score': obj.harmony_stability,
                'name': '조화와 안정',
                'description': '평화롭고 안정적인 환경을 선호하는 성향'
            },
            'authenticity_depth': {
                'score': obj.authenticity_depth,
                'name': '진정성과 깊이',
                'description': '진실된 관계와 의미있는 경험을 추구하는 성향'
            }
        }


class CombinedAnalysisSerializer(serializers.Serializer):
    """성격 분석과 가치관 분석을 통합한 직렬화기"""

    personality = PersonalityAnalysisSerializer(read_only=True)
    values = ValueAnalysisSerializer(read_only=True)

    # 추가 인사이트
    insights = serializers.SerializerMethodField()

    def get_insights(self, obj):
        """분석 결과를 바탕으로 한 인사이트 제공"""
        personality = obj['personality']
        values = obj['values']

        insights = []

        # 영화 취향과 성격의 연관성 설명
        if personality.openness >= 0.7:
            insights.append("SF나 판타지 영화를 좋아하시는 것은 높은 개방성과 연관이 있습니다.")

        if personality.extraversion >= 0.7:
            insights.append("코미디나 액션 영화 선호는 외향적 성격과 일치합니다.")

        if values.creativity_innovation >= 0.7:
            insights.append("창의성을 중시하는 성향이 강해 예술적이고 독창적인 영화를 선호할 가능성이 높습니다.")

        return insights
