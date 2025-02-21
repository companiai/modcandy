from equalizer.models import ChatMessage, FlaggedMessage
from rest_framework import serializers

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'player_name', 'session_id', 'assigned_tox_score', 'flagged', 'created']


class FlaggedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlaggedMessage
        fields = ['id', 'playerName', 'sessionId', 'tox_type', 'message', 'severity', 'created', ]