from equalizer import views
from django.urls import path

urlpatterns = [
    path('transform', views.GetTransformedText.as_view(), name='get-transformed-text'),
    path('basic', views.AnalyzerSimple.as_view(), name='basic-message-tox-score'),
    path('profile', views.AnalyzerProfiler.as_view(), name='profile-based-tox-score'),
]