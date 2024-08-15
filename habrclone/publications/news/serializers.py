from rest_framework import serializers
from ..serializers import PublicationListSerializer
from ..models import User
from .models import News
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

class NewsSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset = User.objects.all())
    mention = serializers.PrimaryKeyRelatedField(many = True, queryset = User.objects.all())
    tags = TagListSerializerField()

    class Meta:
        model = News
        fields = [
            'author', 'mention',
            'status', 'title',
            'intro_text', 'intro_image',
            'tags'
        ]

class NewsEditSerializer(TaggitSerializer, serializers.ModelSerializer):
    mention = serializers.PrimaryKeyRelatedField(many = True, queryset = User.objects.all())
    tags = TagListSerializerField()

    class Meta:
        model = News
        fields = [
            'mention', 'title',
            'intro_text', 'intro_image',
            'tags', 'status'
        ]

class NewsListSerializer(TaggitSerializer, PublicationListSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = News
        exclude = PublicationListSerializer.Meta.exclude
