from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name = 'login'),
    path('logout/', views.LogoutAPIView.as_view(), name = 'logout'),
    path('registration/', views.RegistrationAPIView.as_view(), name = 'registration'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('verify/mail/', views.CodeEmailAPIView.as_view(), name = 'verify'),
    path('edit/', views.EditAPIView.as_view(), name = 'edit'),
    path('password/change/', views.ChangePasswordAPIView.as_view(), name = 'password_change'),
    path('password/reset/', views.PasswordResetAPIView.as_view(), name = 'password_reset'),
    path('password/reset/<str:token>/', views.PasswordResetDoneAPIView.as_view(), name = 'password_reset_done'),
]