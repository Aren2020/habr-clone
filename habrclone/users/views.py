import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, UserEditSerializer, ChangePasswordSerializer
from .models import User
from .tasks import verification_mail

def error_response(errors):
    for field, error_list in errors.items():
        if isinstance(error_list, list) and len(error_list) > 0:
            return {'error': f'{field.capitalize()} - {error_list[0]}'}

class RegistrationAPIView(APIView):

    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            password = data.pop('password')

            user = User.objects.create(**data)
            user.set_password(password)
            user.save()
            
            refresh = RefreshToken.for_user(user)
            refresh.payload.update({
                'user_id': user.id,
                'username': user.username
            })

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status = status.HTTP_201_CREATED)
        
        data = error_response(serializer.errors)
        return Response(data, status = status.HTTP_400_BAD_REQUEST)

class CodeEmailAPIView(APIView):
    '''Send email with random code which check in frontend'''

    def post(self, request):
        data = request.data
        code = random.randint(100000, 1000000)
        verification_mail.delay(data['username'], data['first_name'],
                                data['last_name'], data['email'], code)
        return Response({'code': code},
                        status = status.HTTP_200_OK)

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

        return Response(status = status.HTTP_204_NO_CONTENT)

class EditAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        serializer = UserEditSerializer(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def patch(self, request, pk):
        user = get_object_or_404(User, pk = pk)
        serializer = UserEditSerializer(user, data = request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            if not User.objects.filter(username = username).exclude(pk = pk).exists():
                serializer.save()
                return Response(status = status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Username - Already in use'},
                            status = status.HTTP_400_BAD_REQUEST)

        data = error_response(serializer.errors)
        return Response(data, status = status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = request.user
            
            old_password = data['old_password']
            if not user.check_password(old_password):
                return Response({'error': 'Old password dont match with your current'},
                                status = status.HTTP_400_BAD_REQUEST)
            
            new_password = data['new_password']
            user.set_password(new_password)
            user.save()

            return Response(status = status.HTTP_204_NO_CONTENT)

        data = error_response(serializer.errors)
        return Response(data, status = status.HTTP_400_BAD_REQUEST)

