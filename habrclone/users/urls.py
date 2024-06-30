from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name = 'login'),
    path('logout/', views.LogoutAPIView.as_view(), name = 'logout'),
    path('registration/', views.RegistrationAPIView.as_view(), name = 'registration'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
]