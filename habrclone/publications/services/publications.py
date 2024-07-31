from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from ..models import Content, Post
from ..serializers import PostSerializer

class Publication:
    def __init__(self, publication_type, publication_id):
        self.PUBLICATION_MODEL_NAME = {
            'posts': 'Post',
            'articles': 'Article',
        }
        self.PUBLICATION_MODEL_CLASS = {
            'posts': Post
        }
        self.invalid_publication_type =  (publication_type not in self.PUBLICATION_MODEL_NAME)
        if self.invalid_publication_type:
            return
        
        self.publication_type = publication_type
        self.publication_id = publication_id

        self.model = self.get_model()
        self.publication_serialier = self.get_publication_serialier()

    def get_model(self):
        model_name = self.PUBLICATION_MODEL_NAME[self.publication_type]
        return apps.get_model('publications', model_name)

    def get_publication_serialier(self):
        if self.publication_type == 'posts':
            serializer = PostSerializer
        return serializer

    def get_publication_data(self):
        serializer = self.get_publication_serialier()
        model_class = self.PUBLICATION_MODEL_CLASS[self.publication_type]
        try:
            publication = model_class.objects.get(id = self.publication_id)
        except model_class.DoesNotExist:
            return
        return [{'publication': serializer(publication).data}]

    def list(self):
        pass # prefetch related

    def detail(self):
        """Get all content related to a specific publication."""
        if not self.model:
            return
        
        content_type = ContentType.objects.get_for_model(self.model)
        return Content.objects.filter(
            publication_content_type = content_type,
            publication_object_id = self.publication_id
        )

