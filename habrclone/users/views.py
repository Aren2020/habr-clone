from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import UserSerializer

class RegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            refresh.payload.update({
                'user_id': user.id,
                'username': user.username
            })

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status = status.HTTP_201_CREATED)
        
        errors = serializer.errors
        for field, error_list in errors.items():
            if isinstance(error_list, list) and len(error_list) > 0:
                return Response({'error': error_list[0]}, status = status.HTTP_400_BAD_REQUEST)
            
class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            return Response({'error': 'Login and password fields is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username = username, password = password)
        if not user:
            return Response({'error': 'Invalid data'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
            'user_id': user.id,
            'username': user.username
        })

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status = status.HTTP_200_OK)

class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'},
                            status = status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({'error': 'Incorrect Refresh token'},
                            status = status.HTTP_400_BAD_REQUEST)

        return Response(status = status.HTTP_200_OK)

