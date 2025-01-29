from equalizer.models import ChatMessage, ToxicityIncident
from rest_framework import serializers

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToxicityIncident
        fields = ['incident_id', 'playerName', 'sessionId', 'tox_type', 'severity', 'created']