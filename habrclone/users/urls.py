from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name = 'login'),
    path('logout/', views.LogoutAPIView.as_view(), name = 'logout'),
    path('registration/', views.RegistrationAPIView.as_view(), name = 'registration'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('<int:pk>/edit/', views.EditAPIView.as_view(), name = 'edit'),
    path('verify/mail/', views.CodeEmailAPIView.as_view(), name = 'verify'),
]