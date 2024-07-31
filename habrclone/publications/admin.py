from django.contrib import admin
from .models import Post, Text, File, Image, Video, Content

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'created_at']



@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'publication', 'item']



@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_name', 'content']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_name', 'file']

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_name', 'image']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_name', 'url']