from rest_framework import serializers
from ..serializers import PublicationListSerializer
from ..models import User
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset = User.objects.all())
    mention = serializers.PrimaryKeyRelatedField(many = True, queryset = User.objects.all())

    class Meta:
        model = Post 
        fields = ['author', 'mention', 'status']

class PostEditSerializer(serializers.ModelSerializer):
    mention = serializers.PrimaryKeyRelatedField(many = True, queryset = User.objects.all())

    class Meta:
        model = Post 
        fields = ['mention', 'status']


class PostListSerializer(PublicationListSerializer):

    class Meta:
        model = Post
        exclude = PublicationListSerializer.Meta.exclude

