from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.ListAPIView.as_view(), name = 'list'),
    path('edit/<int:post_id>/', views.EditAPIView.as_view(), name = 'edit')
]