from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..views import PublicationEditAPIView
from .services import ArticleService
from .models import Article
from .serializers import ArticleSerializer

article_service = ArticleService()

class ListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    @swagger_auto_schema(
        operation_description = "Retrieve a list of articles with pagination.",
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
                            "created_at": "2024-08-17T15:01:07.913426Z",
                            "status": True,
                            "title": "Understanding Django Rest Framework",
                            "intro_text": "This article explains the basics of Django Rest Framework and how to create APIs.",
                            "intro_image": None,
                            "level": "easy",
                            "read_time": 2,
                            "views": 6,
                            "rating": -1
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
        articles_data = article_service.list(page_number)
        return Response( articles_data )

    @swagger_auto_schema(
        operation_description = "Create a new article.",
        request_body = ArticleSerializer,
        manual_parameters = [
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING, required = True
            )
        ],
        responses = {
            201: openapi.Response(
                description = "Article created successfully",
            ),
            400: openapi.Response(
                description = "Bad request, validation errors returned",
            ),
        }
    )
    def post(self, request):

        serializer = ArticleSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(author = request.user)
            if serializer.validated_data['status']:
                article_service.add_publication_creation()
            
            return Response(status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
class DetailAPIView(APIView):

    @swagger_auto_schema(
        operation_description = "Get detail information about article.",
        manual_parameters = [
            openapi.Parameter(
                'article_id', openapi.IN_PATH,
                description = 'Article ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ],
        responses = {
            200: openapi.Response(
                description = "Article cget successfully",
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
                            "items": [
                                {
                                    "id": 3,
                                    "item": {
                                      "item_name": "text",
                                      "content": "t2"
                                    }
                                }
                            ],
                            "created_at": "2024-08-17T15:01:07.913426Z",
                            "status": True,
                            "title": "Understanding Django Rest Framework",
                            "intro_text": "This article explains the basics of Django Rest Framework and how to create APIs.",
                            "intro_image": None,
                            "level": "easy",
                            "read_time": 2,
                            "views": 6,
                            "rating": -1
                        }
                    ]
                }
            ),
            404: openapi.Response(
                description = "Article doesnt exists",
            ),
        }
    )
    def get(self, request, article_id):
        data = article_service.detail(article_id)
        if isinstance(data, int):
            return Response(status = data)
        return Response(data)

class EditAPIView(PublicationEditAPIView):

    @swagger_auto_schema(
        operation_description = "Retrieve a article by ID",
        responses = {
            200: ArticleSerializer(),
            404: 'Not Found'
        },
        manual_parameters = [
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING, required = True
            ),
            openapi.Parameter(
                'article_id', openapi.IN_PATH,
                description = 'Article ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def get(self, request, article_id):
        return PublicationEditAPIView.get(self, Article, article_id, ArticleSerializer)

    @swagger_auto_schema(
        operation_description = "Update a article by ID",
        request_body = ArticleSerializer,
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
                'article_id', openapi.IN_PATH,
                description = 'Article ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def put(self, request, article_id):
        return PublicationEditAPIView.put(self, request, Article, article_id, ArticleSerializer)
    
    @swagger_auto_schema(
        operation_description = "Delete a article by ID",
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
                'article_id', openapi.IN_PATH,
                description = 'Article ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def delete(self, request, article_id):
        return PublicationEditAPIView.delete(self, request, Article, article_id)
