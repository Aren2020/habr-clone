from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..views import PublicationEditAPIView
from .services import ArticleService
from .models import Article
from .serializers import ArticleSerializer, ArticleEditSerializer

article_service = ArticleService()

class ListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def get(self, request):
        page_number = request.GET.get('page_number')
        articles_data = article_service.list(page_number)
        return Response( articles_data )

    def post(self, request):

        serializer = ArticleSerializer(data = request.data)
        if serializer.is_valid():

            article = serializer.save(
                author = request.user,
            )
            article.save()
            
            return Response(status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
class DetailAPIView(APIView):
    def get(self, request, article_id):
        data = article_service.detail(article_id)
        if isinstance(data, int):
            return Response(status = data)
        return Response(data)

class EditAPIView(PublicationEditAPIView):

    def get(self, request, article_id):
        return PublicationEditAPIView.get(self, Article, article_id, ArticleEditSerializer)

    def put(self, request, article_id):
        return PublicationEditAPIView.put(self, request, Article, article_id, ArticleEditSerializer)
    
    def delete(self, request, article_id):
        return PublicationEditAPIView.delete(self, request, Article, article_id)
