# analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('personality/analyze/', views.analyze_personality, name='analyze_personality'),
    path('personality/latest/', views.get_latest_analysis, name='get_latest_analysis'),
    path('personality/statistics/', views.get_analysis_statistics, name='get_analysis_statistics'),
]
