from equalizer.models import ChatMessage, ToxicityIncident
from rest_framework import serializers

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['message', 'player_name', 'session_id', 'assigned_tox_score', 'flagged', 'created']


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToxicityIncident
        fields = ['incident_id', 'playerName', 'sessionId', 'tox_type', 'message', 'severity', 'created', ]