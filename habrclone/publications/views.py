from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from publications.posts.models import Post
from publications.news.models import News
from publications.articles.models import Article
from .serializers import TextSerializer, VideoSerializer, ImageSerializer, FileSerializer
from .models import Content

class ContentAbsract(APIView):
    permission_classes = [IsAuthenticated]

    def _get_publication(self, publication_type, publication_id):
        manager = {
            'articles': Article,
            'news': News,
            'posts': Post
        }[publication_type].published

        publication = manager.get(id = publication_id)
        return publication

    def _get_item_serializer(self, model_name):
        return {
            'text': TextSerializer,
            'image': ImageSerializer,
            'video': VideoSerializer,
            'file': FileSerializer,
        }[model_name]

class ContentAPIView(ContentAbsract):

    def post(self, request, publication_type, publication_id, model_name):
        publication = self._get_publication( publication_type, publication_id ) # declared in subclasses
        if publication.author != request.user:
            return Response(status = status.HTTP_400_BAD_REQUEST)

        serializer = self._get_item_serializer( model_name )(data = request.data)
        if serializer.is_valid():
            item = serializer.save()
            Content.objects.create(
                publication = publication,
                item = item
            )   

            return Response(status = status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        

class ContentDetailAPIView(ContentAbsract):
    def get_content(self, user, publication_type, publication_id, content_id):
        
        try:
            publication = self._get_publication( publication_type, publication_id )
            content = Content.objects.get(id = content_id)
            if content.publication != publication:
                return Response(status = status.HTTP_403_FORBIDDEN)
        except (
            Content.DoesNotExist,
            Post.DoesNotExist,
            News.DoesNotExist,
            Article.DoesNotExist    
        ):
            return Response({'error': 'dont found any matches'}, status = status.HTTP_404_NOT_FOUND)
        
        if publication.author != user:
            return Response(status = status.HTTP_403_FORBIDDEN)
        
        return content

    def get(self, request, publication_type, publication_id, model_name, content_id):
        content = self.get_content(request.user, publication_type, publication_id, content_id)
        if not isinstance(content, Content):
            return content # 4XX response
        
        serializer = self._get_item_serializer( model_name )( content.item )
        return Response( serializer.data )
    
    def put(self, request, publication_type, publication_id, model_name, content_id):
        content = self.get_content(request.user, publication_type, publication_id, content_id)
        if not isinstance(content, Content):
            return content # 4XX response
        
        serializer = self._get_item_serializer( model_name )(content.item, data = request.data )
        if serializer.is_valid():
            serializer.save()
            return Response(status = status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, publication_type, publication_id, model_name, content_id):
        content = self.get_content(request.user, publication_type, publication_id, content_id)
        if not isinstance(content, Content):
            return content # 4XX response
        
        content.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class PublicationEditAPIView(APIView):
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