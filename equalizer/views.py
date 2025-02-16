from rest_framework import generics, status, permissions
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from equalizer.analyzer import PerspectiveUtil
from equalizer.util import EqualizerUtil
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from equalizer.models import ToxicityIncident, Player
from equalizer.serializers import IncidentSerializer
from django_filters import rest_framework as filters
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django.db import models

class GetTransformedText(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        perspective_util = PerspectiveUtil(debug=False)
        transformed_text = perspective_util.transform_text(text=data.get('text'))
        return JsonResponse(
            {
                'text': transformed_text
            },
            safe=False,
            status=status.HTTP_200_OK
        )
   
class AnalyzerSimple(generics.GenericAPIView):

    permission_classes = [
        HasAPIKey
    ]

    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        key = request.META["HTTP_AUTHORIZATION"].split()[1]
        api_key = APIKey.objects.get_from_key(key)
        perspective_util = PerspectiveUtil(debug=False)
        if data.get('text', None):
            data, error = perspective_util.simple_tox_score(text=data.get('text'), user=api_key.user_rest_key.user, debug_mode=True)
            if error:
                return JsonResponse(
                    data,
                    safe=False,
                    status=status.HTTP_200_OK
                )
            api_key.user_rest_key.user.user_credit.update_credit_usage(1)
            return JsonResponse(
                data,
                safe=False,
                status=status.HTTP_200_OK
            )
        return JsonResponse(
                {
                    "error": "Missing Fields"
                },
                safe=False,
                status=status.HTTP_400_BAD_REQUEST
            )
    
class AnalyzerProfiler(generics.GenericAPIView):

    permission_classes = [
        HasAPIKey
    ]

    def post(self, request, *args, **kwargs):
        key = request.META["HTTP_AUTHORIZATION"].split()[1]
        api_key = APIKey.objects.get_from_key(key)
        data = JSONParser().parse(request)
        perspective_util = PerspectiveUtil(debug=False)
        if( data.get('playerID', None) and data.get('text', None) and data.get('sessionID', None)):
            data, error = perspective_util.player_tox_score(text=data.get('text'), user=api_key.user_rest_key.user, playerId=data.get('playerID'), sessionId=data.get('sessionID'), playerName=data.get('playerName', ''), debug_mode=False)
            if error:
                return JsonResponse(
                    data,
                    safe=False,
                    status=status.HTTP_200_OK
                )
            api_key.user_rest_key.user.user_credit.update_credit_usage(1)
            return JsonResponse(
                data,
                safe=False,
                status=status.HTTP_200_OK
            )
        return JsonResponse(
                {
                    "error": "Missing Fields"
                },
                safe=False,
                status=status.HTTP_400_BAD_REQUEST
            )
    

class RecentMessage(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs):
        equalizer_util = EqualizerUtil(debug=False)
        data = equalizer_util.get_recent_messages(user=request.user)
        return JsonResponse(
            data,
            safe=False,
            status=status.HTTP_200_OK
        )
    
class SessionMessage(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs):
        equalizer_util = EqualizerUtil(debug=False)
        data = equalizer_util.get_session_messages(user=request.user, sessionid=kwargs.get('sessionid'))
        return JsonResponse(
            data,
            safe=False,
            status=status.HTTP_200_OK
        )

    
class ToxicityIncidentFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    severity = filters.CharFilter(field_name='severity')
    type = filters.CharFilter(field_name='tox_type')
    playerName = filters.CharFilter(field_name='playerName')
    sessionId = filters.CharFilter(field_name='sessionId')
    
    class Meta:
        model = ToxicityIncident
        fields = ['start_date', 'end_date', 'severity', 'type', 'playerName', 'sessionId']

class HTTPSPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        if response.data.get('next'):
            response.data['next'] = response.data['next'].replace('http:', 'https:')
        if response.data.get('previous'):
            response.data['previous'] = response.data['previous'].replace('http:', 'https:')
        return response

class IncidentView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IncidentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ToxicityIncidentFilter
    pagination_class = HTTPSPagination

    def get_queryset(self):
        return ToxicityIncident.objects.filter(user=self.request.user)

class PlayerStatsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get total players count
        total_players = Player.objects.filter(user=request.user).count()
        
        # Get top 10 toxic players by incident count
        top_toxic_players = Player.objects.filter(user=request.user)\
            .annotate(incident_count=models.Count('player_chat_message__message_toxicity_incident'))\
            .order_by('-incident_count')[:10]\
            .values('playerId', 'playerName', 'incident_count', 'player_tox_score')

        return JsonResponse({
            'total_players': total_players,
            'top_toxic_players': list(top_toxic_players)
        }, safe=False, status=status.HTTP_200_OK)

class PlayerIncidentsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HTTPSPagination
    
    def get(self, request, *args, **kwargs):
        player_id = kwargs.get('player_id')
        try:
            player = Player.objects.get(playerId=player_id)
            
            # Get total messages count for the player
            total_messages = player.player_chat_message.count()
            
            incidents = ToxicityIncident.objects.filter(
                user=request.user,
                chat_message__player__playerId=player_id
            )
            
            # Get total sessions and toxic sessions counts
            total_sessions = incidents.values('sessionId').distinct().count()
            toxic_sessions = incidents.filter(
                severity__in=['HIGH', 'MEDIUM']  # Adjust severity levels as needed
            ).values('sessionId').distinct().count()
            
            # Get incident statistics with proper aggregation
            total_incidents = incidents.count()
            
            # Group by type and sum the counts
            incidents_by_type = incidents.values('tox_type')\
                .annotate(count=models.Count('tox_type'))\
                .order_by('-count')  # Sort by count in descending order
            
            # Group by severity and sum the counts
            incidents_by_severity = incidents.values('severity')\
                .annotate(count=models.Count('severity'))\
                .order_by('-count')  # Sort by count in descending order
            
            # Get paginated recent incidents
            paginated_incidents = self.paginate_queryset(
                incidents.order_by('-created')
            )
            
            return JsonResponse({
                'player_id': player.playerId,
                'player_name': player.playerName,
                'tox_score': player.player_tox_score,
                'total_messages': total_messages,
                'total_sessions': total_sessions,
                'toxic_sessions': toxic_sessions,
                'total_incidents': total_incidents,
                'incidents_by_type': list(incidents_by_type),
                'incidents_by_severity': list(incidents_by_severity),
                'recent_incidents': IncidentSerializer(
                    paginated_incidents, 
                    many=True
                ).data
            }, safe=False, status=status.HTTP_200_OK)
            
        except Player.DoesNotExist:
            return JsonResponse({
                'error': 'Player not found'
            }, status=status.HTTP_404_NOT_FOUND)