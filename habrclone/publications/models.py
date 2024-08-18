from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models
from users.models import User

class Content(models.Model):
    publication_content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE,
                                                 related_name = 'publication_content_types',
                                                 limit_choices_to = {'model__in': ('post',
                                                                                   'article',
                                                                                   'news')})
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

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
                      .filter(status = True)

class Publication(models.Model):
    author = models.ForeignKey(User, related_name = '%(class)s_publications',
                               on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    mention = models.ManyToManyField(User, related_name = '%(class)s_mentions',
                                     blank = True)

    # ratings redis and signals
    likes = models.ManyToManyField(User, related_name = '%(class)s_likes',
                                   blank = True)  # user.posts_likes.all()
    dislikes = models.ManyToManyField(User, related_name = '%(class)s_dislikes',
                                      blank = True)
    status = models.BooleanField(default = True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields = ['status']),
        ]

class ItemBase(models.Model):
    creator = models.ForeignKey(User, related_name = '%(class)s_items',
                                on_delete = models.CASCADE)
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
    image = models.ImageField(upload_to = 'images')

class Video(ItemBase):
    url = models.URLField()
