# movies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('search/', views.search_movies, name='search_movies'),
    path('search_and_save/', views.search_and_save_movies, name='search_and_save_movies'),
]
