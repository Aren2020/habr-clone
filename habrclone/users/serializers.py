from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        

    def validate_username(self, username):
        '''Username is unique'''
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This username is already in use.")
        return username

    def validate_email(self, email):
        '''Email is unique'''
        if User.objects.filter(email = email).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email

class UserEditSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User    
        fields = ['username', 'first_name', 'last_name']

class CodeEmailSerializer(serializers.Serializer):
    
    username = serializers.CharField(max_length = 200, required = True)
    first_name = serializers.CharField(max_length = 200, required = True)
    last_name = serializers.CharField(max_length = 200, required = True)
    email = serializers.EmailField(required = True)


class ChangePasswordSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(required = True)
    new_password = serializers.CharField(required = True)

class ResetPasswordSerializer(serializers.Serializer):    
    email = serializers.EmailField(required = True)

class ResetPasswordDoneSerializer(serializers.Serializer):    
    password = serializers.CharField(write_only = True, required = True)