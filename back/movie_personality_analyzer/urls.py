# movie_personality_analyzer/urls.py
from django.contrib import admin
from django.urls import path, include
from movies import views as movie_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/movies/', include('movies.urls')),
    path('api/analysis/', include('analysis.urls')),

    # preferences 전용 URL 패턴 추가 (검색 결과 [31] 패턴)
    path('api/preferences/', movie_views.preferences_handler, name='preferences_api'),
]
