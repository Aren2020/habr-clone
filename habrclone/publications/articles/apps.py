from django.apps import AppConfig
from django.db.models.signals import m2m_changed

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'publications.articles'

    def ready(self):
        from ..signals import likes_changed, dislikes_changed
        from .models import Article

        m2m_changed.connect(likes_changed, sender = Article.likes.through)
        m2m_changed.connect(dislikes_changed, sender = Article.dislikes.through)