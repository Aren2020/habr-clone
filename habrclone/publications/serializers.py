from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Content, Text, Image, File, Video, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 
                  'first_name', 'last_name',
                  'username', 'email']

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ['item_name', 'content']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['item_name', 'image']

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['item_name', 'file']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['item_name', 'url']

    
class ContentSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'item']

    def get_item(self, obj):
        item = obj.item
        if isinstance(item, Text):
            return TextSerializer(item).data
        elif isinstance(item, File):
            return FileSerializer(item).data
        elif isinstance(item, Image):
            return ImageSerializer(item).data
        elif isinstance(item, Video):
            return VideoSerializer(item).data
        return None


class PublicationListSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    mention = UserSerializer(many = True)

    class Meta:
        exclude = ['likes', 'dislikes']

        