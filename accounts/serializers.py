from rest_framework import serializers
from accounts.models import CustomUser, UserAPIKey



# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name']


class UserAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAPIKey
        fields = ['keyname', 'created', 'key_prefix']