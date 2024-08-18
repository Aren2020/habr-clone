from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from publications.posts.models import Post
from publications.news.models import News
from publications.articles.models import Article
from .serializers import TextSerializer, VideoSerializer, ImageSerializer, FileSerializer
from .models import Content, Text, Video, Image, File

class ContentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_item_serializer(self, model_name):
        return {
            'text': TextSerializer,
            'image': ImageSerializer,
            'video': VideoSerializer,
            'file': FileSerializer  
        }[model_name]

    def _get_publication(self, user, publication_type, publication_id):
        model_class = {
            'articles': Article,
            'news': News,
            'posts': Post,
        }[publication_type]

        try:
            publication = model_class.published.get(id = publication_id)
            if publication.author != user:
                return {'error': 'You are not the author of the publication'}, 403
            
            return None, publication
        except model_class.DoesNotExist:
            return {'error': 'Publication doesnt exists'}, 404

    def post(self, request, publication_type, publication_id, model_name):
        error, publication = self._get_publication( request.user, publication_type, publication_id ) # declared in subclasses
        if error:
            return Response(error, status = publication)        

        serializer = self._get_item_serializer( model_name )(data = request.data)
        if serializer.is_valid():
            item = serializer.save(creator = request.user)
            Content.objects.create(
                publication = publication,
                item = item
            )

            return Response(status = status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        

class ItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]


    def _get_item(self, user, model_name, item_id):
        item_class, item_serializer = {
            'text': (Text, TextSerializer),
            'image': (Image, ImageSerializer),
            'video': (Video, VideoSerializer),
            'file': (File, FileSerializer),
        }[model_name]

        item = item_class.objects.get(id = item_id)
        if item.creator != user:
            return {'error': 'You are not the creator'}, 403 

        return item_serializer, item    

    def get(self, request, model_name, item_id):
        item_serializer, item = self._get_item(request.user, model_name, item_id)
        if isinstance(item, int):
            return Response(item_serializer, status = item)
        
        serializer = item_serializer( item )
        return Response( serializer.data )
    
    def put(self, request, model_name, item_id):
        item_serializer, item = self._get_item(request.user, model_name, item_id)
        if isinstance(item, int):
            return Response(item_serializer, status = item)

        serializer = item_serializer( item, data = request.data )
        if serializer.is_valid():
            serializer.save()

            return Response(status = status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, model_name, item_id):
        item_serializer, item = self._get_item(request.user, model_name, item_id)
        if isinstance(item, int):
            return Response(item_serializer, status = item)
        
        model = apps.get_model('publications', model_name)
        model_ct = ContentType.objects.get_for_model(model)
        try:
            Content.objects.get(
                content_type = model_ct,
                object_id = item_id
            ).delete()
            model_ct.model_class().objects.get(id = item_id).delete() # delete item
        except Content.DoesNotExist:
            return Response({'error': 'Item dont exists'}, status = status.HTTP_404_NOT_FOUND)

        return Response(status = status.HTTP_204_NO_CONTENT)

class PublicationEditAPIView(APIView): # used in sub apps
    permission_classes = [IsAuthenticated]

    def get(self, model_class, publication_id, edit_serializer):
        try:
            publication = model_class.objects.get(id = publication_id)
        except model_class.DoesNotExist:
            return Response({'error': 'publication dont exists'}, status = status.HTTP_404_NOT_FOUND)
        
        serializer = edit_serializer(publication)
        return Response( serializer.data )

    def put(self, request, model_class, publication_id, edit_serializer):
        try:
            publication = model_class.objects.get(id = publication_id)
        except model_class.DoesNotExist:
            return Response({'error': 'publication dont exists'}, status = status.HTTP_404_NOT_FOUND)

        if publication.author != request.user:
            return Response({'error': 'you are not author'}, status = status.HTTP_403_FORBIDDEN)

        serializer = edit_serializer(publication, data = request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(status = status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, model_class, publication_id):
        try:
            publication = model_class.objects.get(id = publication_id)
        except model_class.DoesNotExist:
            return Response({'error': 'dont find query'}, status = status.HTTP_404_NOT_FOUND)
    
        if publication.author != request.user:
            return Response({'error': 'you are not the owner of publication'}, status = status.HTTP_403_FORBIDDEN)
    
        publication.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)