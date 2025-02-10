from django.db import models
from accounts.models import CustomUser


class Player(models.Model):
    playerId = models.CharField(max_length=50, unique=True, db_index=True)
    playerName = models.CharField(max_length=50, db_index=True, blank=True)
    player_tox_score = models.IntegerField(default=0)
    tox_weight = models.DecimalField(decimal_places=5, max_digits=8, default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.playerId
    
class Session(models.Model):
    sessionId = models.CharField(max_length=255, unique=True, db_index=True)
    session_tox_score = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.sessionId


class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='user_chat_message', null=True)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, related_name='player_chat_message', null=True)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, related_name='session_chat_message', null=True)
    message = models.CharField(max_length=255, blank=True)
    tox_score = models.IntegerField(default=0)
    assigned_tox_score = models.IntegerField(default=0)
    flagged = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        if self.player:
            return self.player.playerId
        return self.message
    
    @property
    def player_name(self):
        if self.player:
            return self.player.playerName
        return '-'
    
    @property
    def session_id(self):
        if self.session:
            return self.session.sessionId
        return '-'
    
class ToxicityIncident(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='user_toxicity_incident', null=True)
    chat_message = models.ForeignKey(ChatMessage, related_name='message_toxicity_incident', on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, related_name='session_toxicity_incident', null=True)
    playerName = models.CharField(max_length=50, db_index=True, blank=True)
    sessionId = models.CharField(max_length=255, blank=True)
    tox_type = models.CharField(max_length=20, blank=True, db_index=True)
    severity = models.CharField(max_length=20, blank=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.chat_message.message
    
    @property
    def incident_id(self):
        return self.pk
    
    @property
    def message(self):
        return self.chat_message.message
    
    

class PerspectiveAnalysis(models.Model):
    chat_message = models.ForeignKey(ChatMessage, related_name='message_perspective_analysis', on_delete=models.SET_NULL, null=True)
    raw_data = models.TextField(blank=True)
    severe_toxicity = models.DecimalField(decimal_places=10, max_digits=20, default=0)
    sexually_explicit = models.DecimalField(decimal_places=10, max_digits=20, default=0)
    threat = models.DecimalField(decimal_places=10, max_digits=20, default=0)
    profanity = models.DecimalField(decimal_places=10, max_digits=20, default=0)
    toxicity = models.DecimalField(decimal_places=10, max_digits=20, default=0)
    identity_attack = models.DecimalField(decimal_places=10, max_digits=20, default=0)
    insult = models.DecimalField(decimal_places=10, max_digits=20, default=0)
    language = models.CharField(max_length=5, db_index=True, blank=True)
    detected_language = models.CharField(max_length=5, db_index=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.chat_message.message


class BadWordShortForm(models.Model):
    text = models.CharField(max_length=255, db_index=True, unique=True)
    full_form = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.text

