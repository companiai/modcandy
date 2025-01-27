from rest_framework import serializers
from accounts.models import CustomUser



# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name']