from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..views import PublicationEditAPIView
from .serializers import NewsSerializer, NewsEditSerializer
from .services import NewsService
from .models import News

news_service = NewsService()

class ListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def get(self, request):
        page_number = request.GET.get('page_number')
        news_data = news_service.list(page_number)
        return Response( news_data )

    def post(self, request):

        serializer = NewsSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
class DetailAPIView(APIView):
    def get(self, request, news_id):
        data = news_service.detail(news_id)
        if isinstance(data, int):
            return Response(status = data)
        return Response(data)

class EditAPIView(PublicationEditAPIView):

    def get(self, request, news_id):
        return PublicationEditAPIView.get(self, News, news_id, NewsEditSerializer)

    def put(self, request, news_id):
        return PublicationEditAPIView.put(self, request, News, news_id, NewsEditSerializer)
    
    def delete(self, request, news_id):
        return PublicationEditAPIView.delete(self, request, News, news_id)
