from django.contrib import admin
from .models import Movie, UserMoviePreference

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'vote_average', 'popularity']
    list_filter = ['release_date', 'vote_average']
    search_fields = ['title', 'original_title']
    readonly_fields = ['tmdb_id', 'created_at', 'updated_at']

    fieldsets = (
    ('기본 정보', {
        'fields': ('tmdb_id', 'title', 'original_title', 'overview', 'release_date')
    }),
    ('장르 및 분류', {
        'fields': ('genres', 'melodrama_score', 'comic_score', 'violent_score', 'imaginative_score', 'exciting_score')
    }),
    ('메타 정보', {
        'fields': ('poster_path', 'vote_average', 'popularity')
    }),
    ('시스템 정보', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)
    }),
    )

@admin.register(UserMoviePreference)
class UserMoviePreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'movie__title']