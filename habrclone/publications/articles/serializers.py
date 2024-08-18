from rest_framework import serializers
from ..serializers import PublicationListSerializer
from .models import Article
from ..models import User
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    mention = serializers.PrimaryKeyRelatedField(many = True, queryset = User.objects.all())
    tags = TagListSerializerField()

    class Meta:
        model = Article
        fields = [
            'mention', 'status',
            'title',
            'intro_text', 'intro_image',
            'level', 'tags'
        ]

class ArticleListSerializer(TaggitSerializer, PublicationListSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Article
        exclude = PublicationListSerializer.Meta.exclude
