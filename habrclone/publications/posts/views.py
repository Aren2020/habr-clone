from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..views import PublicationEditAPIView
from .serializers import PostSerializer
from .services import PostService
from .models import Post

post_service = PostService()

class ListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    @swagger_auto_schema(
        operation_summary = "Retrieve posts",
        responses = {
            200: openapi.Response(
                description = "A successful response",
                # examples = {
                #     'application/json': 
                # }
            )
        }
    )
    def get(self, request):
        page_number = request.GET.get('page_number')
        posts_data = post_service.list(page_number)
        return Response( posts_data )
    
    def post(self, request):

        serializer = PostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(author = request.user)
            if serializer.validated_data['status']:
                post_service.add_publication_creation()
                
            return Response(status = status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class EditAPIView(PublicationEditAPIView):

    def get(self, request, post_id):
        return PublicationEditAPIView.get(self, Post, post_id, PostSerializer)

    def put(self, request, post_id):
        return PublicationEditAPIView.put(self, request, Post, post_id, PostSerializer)
    
    def delete(self, request, post_id):
        return PublicationEditAPIView.delete(self, request, Post, post_id)