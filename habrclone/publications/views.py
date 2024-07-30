from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .services.publications import Publication
from .serializers import ContentSerializer, get_publiaction_data

class PublicationApiView(APIView):
    ### add error handling

    @swagger_auto_schema(
        operation_summary = "Retrieve publication and its related content",
        operation_description = "Get the details of a publication and its associated items.",
        manual_parameters = [
            openapi.Parameter('type', openapi.IN_PATH, 
                              description = "Type of publication (e.g., 'posts')",
                              type = openapi.TYPE_STRING),
            openapi.Parameter('id', openapi.IN_PATH,
                              description = "ID of the publication",
                              type = openapi.TYPE_INTEGER)
        ],
        responses = {
            200: openapi.Response(
                description = "A successful response",
                examples = {
                    'application/json': {
                        "items": [
                            {
                                "id": 1,
                                "item": {
                                    "item_name": "file",
                                    "file": "/media/files/Allahverdyan_Aren_2_XHCZ5Aw.pdf"
                                }
                            },
                            {
                                "id": 2,
                                "item": {
                                    "item_name": "image",
                                    "image": "/media/images/Снимок_экрана_11-7-2024_213042_localhost.jpeg"
                                }
                            },
                            {
                                "id": 3,
                                "item": {
                                    "item_name": "text",
                                    "content": "Test text"
                                }
                            },
                            {
                                "id": 4,
                                "item": {
                                    "item_name": "video",
                                    "url": "https://youtu.be/V0qAq6ZLpic?si=BnE-UgyZkAP_1INf"
                                }
                            }
                        ],
                        "publication": {
                            "id": 1,
                            "title": "Test Post",
                            "author": {
                                "id": 1,
                                "first_name": "First Name",
                                "last_name": "Last Name",
                                "username": "Aren",
                                "email": "myemail@gmail.com"
                            },
                            "mention": [
                                {
                                    "id": 1,
                                    "first_name": "First Name",
                                    "last_name": "Last Name",
                                    "username": "Aren",
                                    "email": "myemail@gmail.com"
                                }
                            ],
                            "created_at": "2024-07-30T18:32:27.222617Z"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description = "Bad Request",
                examples = {
                    'application/json': {"error": "Invalid publication type"}
                }
            ),
            404: openapi.Response(
                description = "Not Found",
                examples={
                    'application/json': {"error": "Publication not found"}
                }
            )
        }
    )
    def get(self, request, type, id):
        publication = Publication(type)
        publication_data = get_publiaction_data(type, id)
        contents = publication.detail(id)
        serializer = ContentSerializer(contents, many = True)
        print(publication_data, serializer.data)
        data = serializer.data + publication_data
        return Response(data)