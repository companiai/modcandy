from django.contrib import admin
from equalizer.models import Player, Session, ChatMessage, PerspectiveAnalysis, BadWordShortForm, ToxicityIncident

# Register your models here.
class CustomReadOnlyAdmin(admin.ModelAdmin):

    def has_change_permission(self, request, obj=None):
        return False

class PlayerAdmin(CustomReadOnlyAdmin):

    list_display = (
        'playerId',
        'playerName',
        'player_tox_score',
        'tox_weight',
    )

class SessionAdmin(CustomReadOnlyAdmin):

    list_display = (
        'sessionId',
        'session_tox_score',
    )

class ChatMessageAdmin(CustomReadOnlyAdmin):

    list_display = (
        'player',
        'message',
        'tox_score',
        'assigned_tox_score',
        'flagged',
    )

    list_filter = (
        'flagged',
    )

class BadWordListAdmin(admin.ModelAdmin):

    list_display = (
        'text',
        'full_form',
    )
    


admin.site.register(Player, PlayerAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(PerspectiveAnalysis, CustomReadOnlyAdmin)
admin.site.register(BadWordShortForm, BadWordListAdmin)
admin.site.register(ToxicityIncident, CustomReadOnlyAdmin)