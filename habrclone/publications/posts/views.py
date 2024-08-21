from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..views import PublicationEditAPIView
from .serializers import PostSerializer, PostListSerializer
from .services import PostService
from .models import Post

post_service = PostService()

class ListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    @swagger_auto_schema(
        operation_description = "Retrieve a list of posts with pagination.",
        responses = {
            200: openapi.Response(
                description = "A successful response",
                examples = {
                    'application/json':
                        [
                          {
                            "id": 1,
                            "author": {
                              "id": 1,
                              "first_name": "",
                              "last_name": "",
                              "username": "Aren",
                              "email": "",
                              "profile_picture": "/media/images/image_name.jpeg"
                            },
                            "mention": [
                              {
                                "id": 2,
                                "first_name": "string",
                                "last_name": "string",
                                "username": "Allo",
                                "email": "user@example.com",
                                "profile_picture": None
                              }
                            ],
                            "created_at": "2024-08-20T08:00:33.638470Z",
                            "status": True,
                            "items": [
                              {
                                "id": 3,
                                "item": {
                                  "item_name": "text",
                                  "content": "t2"
                                }
                              }
                            ],
                            "views": 31,
                            "rating": 0
                          }
                        ]
                }
            ) 
        },
        
        manual_parameters = [
            openapi.Parameter(
                'page_number', openapi.IN_QUERY,
                description = "Page number for pagination",
                type = openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        page_number = request.GET.get('page_number')
        posts_data = post_service.list(page_number)
        return Response( posts_data )
    
    @swagger_auto_schema(
        operation_description = "Create a new post.",
        request_body = PostSerializer,
        manual_parameters = [
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING, required = True
            )
        ],
        responses = {
            201: openapi.Response(
                description = "Post created successfully",
            ),
            400: openapi.Response(
                description = "Bad request, validation errors returned",
            ),
        }
    )
    def post(self, request):

        serializer = PostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(author = request.user)
            if serializer.validated_data['status']:
                post_service.add_publication_creation()
                
            return Response(status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class EditAPIView(PublicationEditAPIView):

    @swagger_auto_schema(
        operation_description = "Retrieve a post by ID",
        responses = {
            200: PostSerializer(),
            404: 'Not Found'
        },
        manual_parameters = [
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING, required = True
            ),
            openapi.Parameter(
                'post_id', openapi.IN_PATH,
                description = 'Post ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def get(self, request, post_id):
        return PublicationEditAPIView.get(self, Post, post_id, PostSerializer)

    @swagger_auto_schema(
        operation_description = "Update a post by ID",
        request_body = PostSerializer,
        responses = {
            204: 'No Content',
            400: 'Bad Request',
            403: 'Forbidden',
            404: 'Not Found'
        },
        manual_parameters = [
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING, required = True
            ),
            openapi.Parameter(
                'post_id', openapi.IN_PATH,
                description = 'Post ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def put(self, request, post_id):
        return PublicationEditAPIView.put(self, request, Post, post_id, PostSerializer)
    
    @swagger_auto_schema(
        operation_description = "Delete a post by ID",
        responses = {
            204: 'No Content',
            403: 'Forbidden',
            404: 'Not Found'
        },
        manual_parameters = [
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING, required = True
            ),
            openapi.Parameter(
                'post_id', openapi.IN_PATH,
                description = 'Post ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def delete(self, request, post_id):
        return PublicationEditAPIView.delete(self, request, Post, post_id)