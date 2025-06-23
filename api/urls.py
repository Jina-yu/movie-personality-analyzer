from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router: ViewSet을 URL에 자동으로 연결
router = DefaultRouter()
router.register(r'movies', views.MovieViewSet)
router.register(r'preferences', views.UserMoviePreferenceViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # 인증 관련 URL
    path('api-auth/', include('rest_framework.urls')),
    # 성격 분석 API 추가
    path('api/analysis/', include('analysis.urls')),

]
