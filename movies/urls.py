# movies/urls.py (올바른 설정)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('search/', views.search_movies_tmdb, name='search_movies_tmdb'),  # 실제 TMDB 검색
    path('tmdb-status/', views.check_tmdb_status, name='check_tmdb_status'),  # 연결 상태 확인
    path('save-tmdb/', views.save_tmdb_movie, name='save_tmdb_movie'),
    path('preferences/', views.preferences_handler, name='preferences_handler'),
]
