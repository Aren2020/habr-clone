from django.apps import AppConfig
from django.db.models.signals import m2m_changed

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'publications.news'

    def ready(self):
        from ..signals import likes_changed, dislikes_changed
        from .models import News

        m2m_changed.connect(likes_changed, sender = News.likes.through)
        m2m_changed.connect(dislikes_changed, sender = News.dislikes.through)