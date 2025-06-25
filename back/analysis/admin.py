from django.contrib import admin
from .models import PersonalityAnalysis, ValueAnalysis


@admin.register(PersonalityAnalysis)
class PersonalityAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'created_at', 'confidence_score', 'movies_analyzed',
        'openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'
    ]
    list_filter = ['created_at', 'confidence_score', 'movies_analyzed']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'movies_analyzed', 'confidence_score')
        }),
        ('성격 특성 (Big Five)', {
            'fields': ('openness', 'conscientiousness', 'extraversion',
                       'agreeableness', 'neuroticism'),
            'description': '각 특성은 0.0(낮음) ~ 1.0(높음) 범위의 값을 가집니다.'
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ValueAnalysis)
class ValueAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'get_username', 'get_created_at',
        'creativity_innovation', 'social_connection', 'achievement_success',
        'harmony_stability', 'authenticity_depth'
    ]
    list_filter = ['personality_analysis__created_at']

    def get_username(self, obj):
        return obj.personality_analysis.user.username

    get_username.short_description = '사용자'

    def get_created_at(self, obj):
        return obj.personality_analysis.created_at

    get_created_at.short_description = '분석일'

    fieldsets = (
        ('가치관 분석', {
            'fields': ('creativity_innovation', 'social_connection', 'achievement_success',
                       'harmony_stability', 'authenticity_depth'),
            'description': '각 가치관은 0.0(낮음) ~ 1.0(높음) 범위의 값을 가집니다.'
        }),
    )

