from ..services import PublicationService
from django.apps import apps
from ..models import Content
from .models import Post
from ..serializers import ContentSerializer
from django.contrib.contenttypes.models import ContentType
from .serializers import PostListSerializer

class PostService(PublicationService):
    def __init__(self):
        self.publication_app = 'posts'
        self.model_name = 'Post'
        PublicationService.__init__(self)
    
    def _post_data(self, post, contents_data):
        post_data = PostListSerializer(post).data
        post_data.update({ 
            'items': contents_data,
            'views': self._get_publication_view(post.id),
            'rating': self._get_publication_rating(post.id)
        })
        return post_data

    def list(self, posts):
        if not posts:
            return []
        
        prefetched_contents = self._prefetch_contents(posts)
        post_list = []
        for post in posts:
            self._add_publication_view(post.id)
            data = self._post_data(post, prefetched_contents[post.id])
            post_list.append(data)
        return post_list

    def detail(self):
        pass