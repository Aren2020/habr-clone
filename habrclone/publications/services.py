from abc import ABC,abstractmethod 
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from publications.posts.models import Post
from publications.news.models import News
from publications.articles.models import Article
from rest_framework.response import Response
from rest_framework import status
from .models import Content
from .serializers import ContentSerializer
import redis

r = redis.Redis(host = settings.REDIS_HOST,
                port = settings.REDIS_PORT,
                db = settings.REDIS_DB)

class PublicationService(ABC):
    def __init__(self):
        self.model, self.model_ct = self.get_model_and_model_ct(
            self.publication_app,
            self.model_name
        )
        self.text_model, self.text_model_ct = self.get_model_and_model_ct('publications', 'Text')
        self.manager = self.model_ct.model_class().published

    def get_model_and_model_ct(self, publication_app, model_name): # dont delete the parmeters!!!
        model = apps.get_model(publication_app, model_name)
        model_ct = ContentType.objects.get_for_model(model)
        return model, model_ct

    def _get_all_publications(self, page_number = 1):
        ## add when user is auth dont recommend him his publications

        ## add algorithm or smth else for recommendation

        publications_list = self.manager.defer('likes', 'dislikes').select_related('author')
        
        if self.publication_app != 'posts':
            publications_list = publications_list.prefetch_related('mention', 'tags')    
        else:
            publications_list = publications_list.prefetch_related('mention')    

        paginator = Paginator(publications_list, 4)
        try:
            publications = paginator.page(page_number)
        except PageNotAnInteger:
            # If page_number is not an integer deliver the first page
            publications = paginator.page(1)
        except EmptyPage:
            # If page_number is out of range return None
            return None
        return publications.object_list
    
    def _prefetch_contents(self, publications):
        publications_ids = publications.values_list('id', flat = True)
        contents = self._get_publication_contents(publications_ids)

        prefetched_contents = {publication_id: [] for publication_id in publications_ids}
        for content in contents:
            publication_id = content.publication_object_id
            content_data = ContentSerializer(content).data
            prefetched_contents[publication_id].append(content_data)
        return prefetched_contents
        
    def _get_publication_key(self, publication_id):
        return f'{self.publication_app}:{publication_id}'

    def _get_publication_contents(self, publications_ids):
        return Content.objects.filter(
            publication_content_type = self.model_ct,
            publication_object_id__in = publications_ids
        ).prefetch_related('item')

    def _add_publication_view(self, publication_id):
        publication_key = self._get_publication_key(publication_id)
        publication_views = f'{publication_key}:views'
        r.incr(publication_views)

    def _get_publication_view(self, publication_id):
        publication_key = self._get_publication_key(publication_id)
        publication_views = f'{publication_key}:views'
        views = r.get(publication_views)
        if not views:
            return 0
        return int( views.decode()) # binary string to int


    def _get_publication_rating(self, publication_id):
        publication_key = self._get_publication_key(publication_id)
        publication_rating_key = f'{publication_key}:rating'
        publication_rating = r.get(publication_rating_key)
        if not publication_rating:
            return 0
        
        rating = int( publication_rating.decode() ) # binary string to number
        return rating 

    def _get_publication_read_time(self, publication_id, contents_dict = {}):
        
        if publication_id not in contents_dict:
            return 2 
        contents = contents_dict[publication_id]

        read_time = 2 # initial minutes 
        for content in contents:
            text = content.item.content
            words_count = len( text.split() )
            read_time += words_count // 180 # 180 words per minute

        return read_time

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def detail(self):
        pass