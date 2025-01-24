from equalizer.models import ChatMessage
from rest_framework import serializers

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'