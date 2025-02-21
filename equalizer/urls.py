from equalizer import views
from django.urls import path

urlpatterns = [
    path('transform', views.GetTransformedText.as_view(), name='get-transformed-text'),
    path('basic', views.AnalyzerSimple.as_view(), name='basic-message-tox-score'),
    path('profile', views.AnalyzerProfiler.as_view(), name='profile-based-tox-score'),
    path('messages/recent', views.RecentMessage.as_view(), name='get-recent-messages'),
    path('messages/session/<str:sessionid>', views.SessionMessage.as_view(), name='get-session-messages'),
    path('list/flagged', views.FlaggedMessageView.as_view(), name='flagged-messages'),
    path('stats/players', views.PlayerStatsView.as_view(), name='player-stats'),
    path('stats/players/<str:player_id>/incidents', views.PlayerFlaggedMessagesView.as_view(), name='player-incidents'),
    path('stats/sessions', views.SessionStatsView.as_view(), name='session-stats'),
    path('stats/system', views.SystemStatsView.as_view(), name='system-stats'),
    path('stats/sessions/<str:sessionid>', views.SessionDetailView.as_view(), name='session-detail'),
]
