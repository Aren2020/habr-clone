from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from users.models import User


class Publication(models.Model):
    author = models.ForeignKey(User, related_name = '%(class)s_publications',
                               on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    mention = models.ManyToManyField(User, related_name = '%(class)s_mentions')
    
    title = models.CharField(max_length = 200)
    # views redis db
    # tags = 
    
    class Meta:
        abstract = True


class Post(Publication):
    pass

class Article(Publication):
    pass


class Content(models.Model):
    publication_content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE,
                                                 related_name = 'publication_content_types',
                                                 limit_choices_to = {'model__in': ('post',
                                                                                   'article')})
    publication_object_id = models.PositiveIntegerField()
    publication = GenericForeignKey('publication_content_type', 'publication_object_id')

    content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE,
                                     related_name = 'content_types',
                                     limit_choices_to = {'model__in': ('text',
                                                                       'video',
                                                                       'image', 
                                                                       'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

class ItemBase(models.Model):
    item_name = models.CharField(max_length = 5, blank = True, default = '')

    def save(self, *args, **kwargs):
        self.item_name = self.__class__.__name__.lower()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True

class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to = 'files')

class Image(ItemBase):
    image = models.FileField(upload_to = 'images')

class Video(ItemBase):
    url = models.URLField()
