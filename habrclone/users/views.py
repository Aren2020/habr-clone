import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from .serializers import (UserSerializer, UserEditSerializer, ChangePasswordSerializer, 
                          ResetPasswordSerializer, ResetPasswordDoneSerializer, CodeEmailSerializer)
from .models import User, PasswordReset
from .tasks import verification_mail,  password_reset_mail

def error_response(errors):
    for field, error_list in errors.items():
        if isinstance(error_list, list) and len(error_list) > 0:
            return {'error': f'{field.capitalize()} - {error_list[0]}'}

class RegistrationAPIView(APIView):
    
    @swagger_auto_schema(
        operation_description = 'User Registration Endpoint',
        request_body = UserSerializer,
        responses = {
            201: 'Successful registration',
            400: 'Invalid data provided',
        }
    )
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

    @swagger_auto_schema(
        operation_description = 'Send verifcation code to the user email',
        request_body = CodeEmailSerializer,
        responses = {
            201: 'Email is successfully sended',
            400: 'Invalid data provided',
        }
    )
    def post(self, request):
        serializer = CodeEmailSerializer(data = request.data)
        if serializer.is_valid():
            data = request.data
            code = random.randint(100000, 1000000)
            full_name = f'{data["first_name"]} {data["last_name"]}' or data['username']
            verification_mail.delay(data['username'], full_name,
                                    data['email'], code)
            return Response({'code': code},
                            status = status.HTTP_200_OK)
        
        data = error_response(serializer.errors)
        return Response(data, status = status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):

    @swagger_auto_schema(
        operation_description = 'User Authentication Endpoint',
        request_body = openapi.Schema(
            type = openapi.TYPE_OBJECT,
            required = ['username', 'password'],
            properties = {
                'username': openapi.Schema(type = openapi.TYPE_STRING),
                'password': openapi.Schema(type = openapi.TYPE_STRING)
            },
        ),
        responses = {
            200: openapi.Response('Successful authentication', schema = openapi.Schema(
                type = openapi.TYPE_OBJECT,
                properties = {
                    'refresh': openapi.Schema(type = openapi.TYPE_STRING),
                    'access': openapi.Schema(type = openapi.TYPE_STRING),
                }
            )),
            400: 'Login and password fields are required',
            401: 'Invalid data',
        }
    )
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

    @swagger_auto_schema(
        operation_description = 'User Logout Endpoint',
        request_body = openapi.Schema(
            type = openapi.TYPE_OBJECT,
            required = ['refresh_token'],
            properties = {
                'refresh_token': openapi.Schema(type = openapi.TYPE_STRING)
            },
        ),
        responses = {
            204: 'Successfully logged out',
            400: 'Bad refresh token or token absence',
        }
    )
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

    @swagger_auto_schema(
        operation_description = 'Retrieve user details',
        responses = {
            200: openapi.Response('User details', UserEditSerializer),
        },
        manual_parameters = [
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING,
                required = True
            ),
        ]
    )
    def get(self, request):
        serializer = UserEditSerializer(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description = 'Update user details',
        request_body = UserEditSerializer,
        responses = {
            204: 'User details updated successfully',
            400: 'Invalid data provided or username already in use',
        },
        manual_parameters = [
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING,
                required = True
            ),
        ]
    )
    def patch(self, request):
        user = request.user
        serializer = UserEditSerializer(user, data = request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            if not User.objects.filter(username = username).exclude(pk = user.pk).exists():
                serializer.save()
                return Response(status = status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Username - Already in use'},
                            status = status.HTTP_400_BAD_REQUEST)

        data = error_response(serializer.errors)
        return Response(data, status = status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description = 'Change user password',
        request_body = ChangePasswordSerializer,
        responses = {
            204: 'Password changed successfully',
            400: 'Invalid data provided or old password does not match',
        },
        manual_parameters = [
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description = 'Bearer <token>',
                type = openapi.TYPE_STRING,
                required = True
            ),
        ]
    )
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
            update_session_auth_hash(request, user)

            return Response(status = status.HTTP_204_NO_CONTENT)

        data = error_response(serializer.errors)
        return Response(data, status = status.HTTP_400_BAD_REQUEST)

class PasswordResetAPIView(APIView):

    @swagger_auto_schema(
        operation_description = 'Send email for password reset',
        request_body = ResetPasswordSerializer,
        responses = {
            204: 'Password reset initiated successfully',
            400: 'Invalid data provided or user with specified email does not exist',
        }
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email = email)

            if user:
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                reset = PasswordReset(email = email, token = token)
                reset.save()

                reset_url = f"{settings.FRONTEND_PASSWORD_RESET_URL}?token={token}"
                password_reset_mail.delay(user.username, user.get_full_name(), email, reset_url)

                return Response(status = status.HTTP_204_NO_CONTENT)
        
        data = error_response(serializer.errors)
        return Response(data, status = status.HTTP_400_BAD_REQUEST)

class PasswordResetDoneAPIView(APIView):
    
    @swagger_auto_schema(
        operation_description = 'Complete password reset',
        request_body = openapi.Schema(
            type = openapi.TYPE_OBJECT,
            properties = {
                'password': openapi.Schema(type = openapi.TYPE_STRING),
            },
            required = ['password'],
        ),
        responses = {
            204: 'Password reset successfully completed',
            400: 'Invalid data provided or invalid token',
            404: 'No user found for the provided token',
        }
    )
    def post(self, request, token):
        serializer = ResetPasswordDoneSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            reset_obj = PasswordReset.objects.get(token = token)
            if not reset_obj:
                return Response({'error':'Invalid token'}, status = status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(email = reset_obj.email)
            if not user:
                return Response({'error':'No user found'}, status = status.HTTP_404_NOT_FOUND)
            user.set_password(data['password'])
            user.save()
            reset_obj.delete()

            return Response(status = status.HTTP_204_NO_CONTENT)

        data = error_response(serializer.errors)
        return Response(data, status = status.HTTP_400_BAD_REQUEST)


