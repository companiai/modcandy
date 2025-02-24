from django.urls import path
from accounts import views as api
from knox import views as knox_views

urlpatterns = [
    path('api/auth/login', api.LoginView.as_view(), name='user-login'),
    path('api/auth/user', api.UserAPI.as_view(), name='user-detail'),
    path('api/auth/register', api.RegisterAPI.as_view(), name='user-register'),
    path('api/key', api.APIKeyView.as_view(), name='api-key'),
    path('api/credit', api.UserCreditUsageView.as_view(), name='credit-usage'),
]