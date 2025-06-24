from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class PersonalityAnalysis(models.Model):
    """사용자의 성격 분석 결과를 저장하는 모델"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자")

    # Big Five 성격 특성 점수 (0.0 ~ 1.0)
    openness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="개방성",
        help_text="새로운 경험과 창의성에 대한 개방 정도"
    )
    conscientiousness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="성실성",
        help_text="책임감과 계획성 정도"
    )
    extraversion = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="외향성",
        help_text="사교성과 활동성 정도"
    )
    agreeableness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="친화성",
        help_text="협조성과 신뢰성 정도"
    )
    neuroticism = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="신경성",
        help_text="감정적 안정성 정도"
    )

    # 분석에 사용된 영화 수
    movies_analyzed = models.IntegerField(verbose_name="분석된 영화 수")

    # 신뢰도 점수 (분석의 정확도 추정치)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="신뢰도 점수"
    )

    # 분석 일시
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="분석 일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정 일시")

    class Meta:
        verbose_name = "성격 분석"
        verbose_name_plural = "성격 분석들"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 성격 분석 ({self.created_at.strftime('%Y-%m-%d')})"

    @property
    def personality_summary(self):
        """성격 특성 요약"""
        traits = {
            '개방성': self.openness,
            '성실성': self.conscientiousness,
            '외향성': self.extraversion,
            '친화성': self.agreeableness,
            '신경성': self.neuroticism
        }
        # 가장 높은 특성 찾기
        dominant_trait = max(traits, key=traits.get)
        return f"주요 특성: {dominant_trait} ({traits[dominant_trait]:.2f})"


    


class ValueAnalysis(models.Model):
    """사용자의 가치관 분석 결과"""

    personality_analysis = models.OneToOneField(
        PersonalityAnalysis,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name="성격 분석"
    )

    # 핵심 가치관들
    creativity_innovation = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="창의성과 혁신"
    )
    social_connection = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="사회적 연결"
    )
    achievement_success = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="성취와 성공"
    )
    harmony_stability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="조화와 안정"
    )
    authenticity_depth = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="진정성과 깊이"
    )

    class Meta:
        verbose_name = "가치관 분석"
        verbose_name_plural = "가치관 분석들"

    def __str__(self):
        return f"{self.personality_analysis.user.username}의 가치관 분석"

    @property
    def top_values(self):
        """상위 3개 가치관 반환"""
        values = {
            '창의성과 혁신': self.creativity_innovation,
            '사회적 연결': self.social_connection,
            '성취와 성공': self.achievement_success,
            '조화와 안정': self.harmony_stability,
            '진정성과 깊이': self.authenticity_depth
        }
        return sorted(values.items(), key=lambda x: x[1], reverse=True)[:3]
