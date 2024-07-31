from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Content, Post, Text, Image, File, Video, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 
                  'first_name', 'last_name',
                  'username', 'email']


class PublicationSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    mention = UserSerializer(many = True)
    class Meta:
        model = Post
        fields = ['id', 'author', 'mention', 'created_at'] # add author and mention

class PostSerializer(PublicationSerializer):
    pass

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

class GenericRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Text):
            serializer = TextSerializer(value)
        elif isinstance(value, File):
            serializer = FileSerializer(value)
        elif isinstance(value, Image):
            serializer = ImageSerializer(value)
        elif isinstance(value, Video):
            serializer = VideoSerializer(value)
        return serializer.data

    def to_internal_value(self, data):
        model = data.get('item_name')
        model_class = ContentType.objects.get(model = model).model_class()

        try:
            return model_class.objects.get(id = data.get('id'))
        except model_class.DoesNotExist:
            raise serializers.ValidationError(f"No {model} found with the ID {data.get('id')}")
    
class ContentSerializer(serializers.ModelSerializer):
    item = GenericRelatedField(read_only = True)

    class Meta:
        model = Content
        fields = ['id', 'item']