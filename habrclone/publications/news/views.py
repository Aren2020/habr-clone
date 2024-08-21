from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ..views import PublicationEditAPIView
from .serializers import NewsSerializer
from .services import NewsService
from .models import News

news_service = NewsService()

class ListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    @swagger_auto_schema(
        operation_description = "Retrieve a list of news with pagination.",
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
                            "tags": [
                                "tg1",
                                "tg2"
                            ],
                            "created_at": "2024-08-20T11:28:48.010700Z",
                            "status": True,
                            "title": "title",
                            "intro_text": "intro",
                            "intro_image": "/media/images/image_name.jpeg",
                            "read_time": 2,
                            "views": 10,
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
        news_data = news_service.list(page_number)
        return Response( news_data )

    @swagger_auto_schema(
        operation_description = "Create a new news.",
        request_body = NewsSerializer,
        manual_parameters = [
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING, required = True
            )
        ],
        responses = {
            201: openapi.Response(
                description = "News created successfully",
            ),
            400: openapi.Response(
                description = "Bad request, validation errors returned",
            ),
        }
    )
    def post(self, request):

        serializer = NewsSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(author = request.user)
            if serializer.validated_data['status']:
                news_service.add_publication_creation()

            return Response(status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
class DetailAPIView(APIView):
    @swagger_auto_schema(
        operation_description = "Get detail information about News",
        manual_parameters = [
            openapi.Parameter(
                'news_id', openapi.IN_PATH,
                description = 'News ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ],
        responses = {
            200: openapi.Response(
                description = "News get successfully",
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
                            "intro_text": "This news explains the basics of Django Rest Framework and how to create APIs.",
                            "intro_image": None,
                            "read_time": 2,
                            "views": 6,
                            "rating": -1
                        }
                    ]
                }
            ),
            404: openapi.Response(
                description = "News doesnt exists",
            ),
        }
    )
    def get(self, request, news_id):
        data = news_service.detail(news_id)
        if isinstance(data, int):
            return Response(status = data)
        return Response(data)

class EditAPIView(PublicationEditAPIView):

    @swagger_auto_schema(
        operation_description = "Retrieve a news by ID",
        responses = {
            200: NewsSerializer(),
            404: 'Not Found'
        },
        manual_parameters = [
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING, required = True
            ),
            openapi.Parameter(
                'news_id', openapi.IN_PATH,
                description = 'News ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def get(self, request, news_id):
        return PublicationEditAPIView.get(self, News, news_id, NewsSerializer)

    @swagger_auto_schema(
        operation_description = "Update a news by ID",
        request_body = NewsSerializer,
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
                'news_id', openapi.IN_PATH,
                description = 'News ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def put(self, request, news_id):
        return PublicationEditAPIView.put(self, request, News, news_id, NewsSerializer)
    
    @swagger_auto_schema(
        operation_description = "Delete a news by ID",
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
                'news_id', openapi.IN_PATH,
                description = 'News ID',
                type = openapi.TYPE_INTEGER, required = True
            )
        ]
    )
    def delete(self, request, news_id):
        return PublicationEditAPIView.delete(self, request, News, news_id)
