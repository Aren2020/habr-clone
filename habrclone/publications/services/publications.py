from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from ..models import Content

class Publication:
    def __init__(self, publication_type):
        self.model = self.get_model(publication_type)

    def get_model(self, publication_type):
        PUBLICATION_MODEL_NAME = {
            'posts': 'Post',
            'articles': 'Article',
        }

        model_name = PUBLICATION_MODEL_NAME[publication_type]
        return apps.get_model('publications', model_name)

    def list(self):
        pass # prefetch related

    def detail(self, publication_id):
        """Get all content related to a specific publication."""

        content_type = ContentType.objects.get_for_model(self.model)
        return Content.objects.filter(
            publication_content_type = content_type,
            publication_object_id = publication_id
        )

