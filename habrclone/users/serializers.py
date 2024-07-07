from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def validate_username(self, username):
        '''username is unique'''
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This username is already in use.")
        return username

class UserEditSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

class ChangePasswordSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(required = True)
    new_password = serializers.CharField(required = True)
