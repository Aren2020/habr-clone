from django.urls import path, include
from . import views

app_name = 'publications'

urlpatterns = [
    path('contents/<publication_type>/<int:publication_id>/<model_name>/',
          views.ContentAPIView.as_view(), name = 'content_create'),
    path('contents/<publication_type>/<int:publication_id>/<model_name>/<int:content_id>/',
          views.ContentDetailAPIView.as_view(), name = 'content_detail'),

    path('posts/', include('publications.posts.urls', namespace = 'posts')),
    path('articles/', include('publications.articles.urls', namespace = 'articles')),
    path('news/', include('publications.news.urls', namespace = 'news')),
]