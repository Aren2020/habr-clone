from django.urls import path, include
from . import views

app_name = 'publications'

urlpatterns = [
    path('contents/<publication_type>/<int:publication_id>/<model_name>/',
          views.ContentAPIView.as_view(), name = 'content_create'),
    path('items/<model_name>/<int:item_id>/',
          views.ItemDetailAPIView.as_view(), name = 'item_detail'),

    path('posts/', include('publications.posts.urls', namespace = 'posts')),
    path('articles/', include('publications.articles.urls', namespace = 'articles')),
    path('news/', include('publications.news.urls', namespace = 'news')),
]