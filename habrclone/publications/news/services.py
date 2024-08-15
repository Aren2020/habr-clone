from ..services import PublicationService
from ..serializers import ContentSerializer
from .serializers import NewsListSerializer
from .models import News

class NewsService(PublicationService):
    def __init__(self):
        self.publication_app = 'news'
        self.model_name = 'News'
        PublicationService.__init__(self)

    def list(self, page_number):
        news = self._get_all_publications(page_number)
        if not news:
            return []

        news_ids = news.values_list('id', flat = True)
        contents = self._get_publication_contents(news_ids).filter(
            content_type = self.text_model_ct
        )
        contents_dict = {}
    
        # Organize contents by publication_id
        for content in contents:
            publication_id = content.publication_object_id
            if publication_id not in contents_dict:
                contents_dict[publication_id] = []
            contents_dict[publication_id].append(content)

        news_data = []
        for new in news:
            new_data = NewsListSerializer(new).data
            new_data.update({ 
                'read_time': self._get_publication_read_time(new.id, contents_dict),
                'views': self._get_publication_view(new.id),
                'rating': self._get_publication_rating(new.id),
            })

            news_data.append(new_data)
        return news_data

    def detail(self, news_id):
        try:
            news = self.manager.get(id = news_id)
        except News.DoesNotExist:
            return 404

        self._add_publication_view(news_id)

        contents = self._get_publication_contents([news_id])
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

        
        news_data = NewsListSerializer(news).data
        news_data.update({ 
            'items': contents_data,
            'read_time': self._get_publication_read_time(news_id, contents_dict),
            'views': self._get_publication_view(news_id),
            'rating': self._get_publication_rating(news_id),
        })

        return news_data

