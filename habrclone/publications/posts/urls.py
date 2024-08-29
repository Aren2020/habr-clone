from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.ListAPIView.as_view(), name = 'list'),
    path('mine/', views.MineAPIView.as_view(), name = 'mine'),
    path('edit/<int:post_id>/', views.EditAPIView.as_view(), name = 'edit')
]