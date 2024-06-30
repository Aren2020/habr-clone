from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate_username(self, username):
        '''username is unique'''
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This username is already in use.")
        return username