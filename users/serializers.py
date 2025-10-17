from .models import UsersModel
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    short_name = serializers.CharField(source='get_short_name', read_only=True)
    
    class Meta:
        model = UsersModel
        exclude = ('password',)

class TeacherModelSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    short_name = serializers.CharField(source='get_short_name', read_only=True)

    class Meta:
        model = UsersModel
        fields = ['first_name', 'short_name', 'last_name', 'full_name', 'color', 'phone_number']