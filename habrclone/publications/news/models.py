from django.db import models
from ..models import Publication
from taggit.managers import TaggableManager

class News(Publication):
    title = models.CharField(max_length = 250)
    intro_text = models.TextField()
    intro_image = models.ImageField(upload_to = 'images', 
                                    null = True, blank = True)

    tags = TaggableManager()

    class Meta:
        verbose_name_plural = 'News'