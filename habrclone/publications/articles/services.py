from ..services import PublicationService
from ..serializers import ContentSerializer
from .serializers import ArticleListSerializer
from django.db import connection
from .models import Article

class ArticleService(PublicationService):
    def __init__(self):
        self.publication_app = 'articles'
        self.model_name = 'Article'
        PublicationService.__init__(self)

    def list(self, articles):
        if not articles:
            return []        

        articles_ids = articles.values_list('id', flat = True)
        contents = self._get_publication_contents(articles_ids).filter(
            content_type = self.text_model_ct
        )
        contents_dict = {}

        # Organize contents by publication_id
        for content in contents:
            publication_id = content.publication_object_id
            if publication_id not in contents_dict:
                contents_dict[publication_id] = []
            contents_dict[publication_id].append(content)


        articles_data = []
        for article in articles:
            article_data = ArticleListSerializer(article).data
            article_data.update({ 
                'read_time': self._get_publication_read_time(article.id, contents_dict),
                'views': self._get_publication_view(article.id),
                'rating': self._get_publication_rating(article.id),
            })

            articles_data.append(article_data)
        
        return articles_data
        
    def detail(self, article_id):
        try:
            article = self.manager.get(id = article_id)
        except Article.DoesNotExist:
            return 404

        self._add_publication_view(article_id)

        contents = self._get_publication_contents([article_id])
        contents_text = contents.filter(
            content_type = self.text_model_ct
        )

        # Organize contents by publication_id
        contents_data = []
        contents_dict = {}
        for content in contents_text:
            content_data = ContentSerializer(content).data
            contents_data.append(content_data)

            publication_id = content.publication_object_id
            if publication_id not in contents_dict:
                contents_dict[publication_id] = []
            contents_dict[publication_id].append(content)

        article_data = ArticleListSerializer(article).data
        article_data.update({ 
            'items': contents_data,
            'read_time': self._get_publication_read_time(article_id, contents_dict),
            'views': self._get_publication_view(article_id),
            'rating': self._get_publication_rating(article_id),
        })

        return article_data
