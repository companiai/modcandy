from rest_framework import serializers
from accounts.models import CustomUser, UserAPIKey



# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'is_verified']


class UserAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAPIKey
        fields = ['keyname', 'created', 'key_prefix']

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validate_data):
        user = CustomUser.objects.create_user(
            email=validate_data['email'], password=validate_data['password'], username=validate_data['email'])
        return user