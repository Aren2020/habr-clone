from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.ListAPIView.as_view(), name = 'list'),
    path('<int:news_id>/', views.DetailAPIView.as_view(), name = 'detail'),
    path('mine/', views.MineAPIView.as_view(), name = 'mine'),
    path('edit/<int:news_id>/', views.EditAPIView.as_view(), name = 'edit'),
]    