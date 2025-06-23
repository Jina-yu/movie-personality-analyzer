# movie_personality_analyzer/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/movies/', include('movies.urls')),  # ← 이 줄만 주석 해제
    # path('api/analysis/', include('analysis.urls')),  # ← 아직 주석 유지
]
