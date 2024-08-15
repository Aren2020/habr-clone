from django.db import models
from ..models import Publication
from taggit.managers import TaggableManager

class Article(Publication):

    class Level(models.TextChoices):
        EASY = 'easy', 'Easy'
        MID = 'mid', 'Mid'
        HARD = 'hard', 'Hard'

    title = models.CharField(max_length = 250)
    intro_text = models.TextField()
    intro_image = models.ImageField(upload_to = 'images',
                                    blank = True, null = True)
    level = models.CharField(max_length = 4,
                             choices = Level.choices,
                             default = Level.EASY)
    
    tags = TaggableManager()