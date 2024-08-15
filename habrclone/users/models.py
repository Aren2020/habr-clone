from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to = 'images', blank = True)
    created = models.DateTimeField(auto_now_add = True)

class PasswordReset(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length = 100)
    created_at = models.DateTimeField(auto_now_add = True)