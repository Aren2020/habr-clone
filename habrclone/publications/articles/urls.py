from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.ListAPIView.as_view(), name = 'list'),
    path('<int:article_id>/', views.DetailAPIView.as_view(), name = 'detail'),
    path('edit/<int:article_id>/', views.EditAPIView.as_view(), name = 'edit'),
]