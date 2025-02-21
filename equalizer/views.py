from rest_framework import generics, status, permissions
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from equalizer.analyzer import PerspectiveUtil
from equalizer.util import EqualizerUtil
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from equalizer.models import FlaggedMessage, Player, Session, ChatMessage
from equalizer.serializers import FlaggedMessageSerializer
from django_filters import rest_framework as filters
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django.db import models
from django.conf import settings

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
            data, error = perspective_util.player_tox_score(text=data.get('text'), user=api_key.user_rest_key.user, playerId=data.get('playerID'), sessionId=data.get('sessionID'), playerName=data.get('playerName', ''), debug_mode=settings.DEBUG_MODE)
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

    
class FlaggedMessageFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    severity = filters.CharFilter(field_name='severity')
    type = filters.CharFilter(field_name='tox_type')
    playerName = filters.CharFilter(field_name='playerName')
    sessionId = filters.CharFilter(field_name='sessionId')
    
    class Meta:
        model = FlaggedMessage
        fields = ['start_date', 'end_date', 'severity', 'type', 'playerName', 'sessionId']

class HTTPSPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        if response.data.get('next'):
            response.data['next'] = response.data['next'].replace('http:', 'https:')
        if response.data.get('previous'):
            response.data['previous'] = response.data['previous'].replace('http:', 'https:')
        return response

class FlaggedMessageView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FlaggedMessageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FlaggedMessageFilter
    pagination_class = HTTPSPagination

    def get_queryset(self):
        return FlaggedMessage.objects.filter(user=self.request.user)

class PlayerStatsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get total players count
        total_players = Player.objects.filter(user=request.user).count()
        
        # Get top 10 toxic players by incident count
        top_toxic_players = Player.objects.filter(user=request.user)\
            .annotate(incident_count=models.Count('player_chat_message__message_flagged_message'))\
            .order_by('-incident_count')[:10]\
            .values('playerId', 'playerName', 'incident_count', 'player_tox_score')

        return JsonResponse({
            'total_players': total_players,
            'top_toxic_players': list(top_toxic_players)
        }, safe=False, status=status.HTTP_200_OK)

class PlayerFlaggedMessagesView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HTTPSPagination
    
    def get(self, request, *args, **kwargs):
        player_id = kwargs.get('player_id')
        try:
            player = Player.objects.get(playerId=player_id)
            
            # Get total messages count for the player
            total_messages = player.player_chat_message.count()
            
            flagged_messages = FlaggedMessage.objects.filter(
                user=request.user,
                chat_message__player__playerId=player_id
            )
            
            # Get total sessions and toxic sessions counts
            total_sessions = flagged_messages.values('sessionId').distinct().count()
            toxic_sessions = flagged_messages.filter(
                severity__in=['HIGH', 'MEDIUM']  # Adjust severity levels as needed
            ).values('sessionId').distinct().count()
            
            # Get incident statistics with proper aggregation
            total_flagged_messages = flagged_messages.count()
            
            # Group by type and sum the counts
            flagged_messages_by_type = flagged_messages.values('tox_type')\
                .annotate(count=models.Count('tox_type'))\
                .order_by('-count')  # Sort by count in descending order
            
            # Group by severity and sum the counts
            flagged_messages_by_severity = flagged_messages.values('severity')\
                .annotate(count=models.Count('severity'))\
                .order_by('-count')  # Sort by count in descending order
            
            # Get paginated recent incidents
            paginated_incidents = self.paginate_queryset(
                flagged_messages.order_by('-created')
            )
            
            return JsonResponse({
                'player_id': player.playerId,
                'player_name': player.playerName,
                'tox_score': player.player_tox_score,
                'total_messages': total_messages,
                'total_sessions': total_sessions,
                'toxic_sessions': toxic_sessions,
                'total_flagged_messages': total_flagged_messages,
                'flagged_messages_by_type': list(flagged_messages_by_type),
                'flagged_messages_by_severity': list(flagged_messages_by_severity),
                'recent_flagged_messages': FlaggedMessageSerializer(
                    paginated_incidents, 
                    many=True
                ).data
            }, safe=False, status=status.HTTP_200_OK)
            
        except Player.DoesNotExist:
            return JsonResponse({
                'error': 'Player not found'
            }, status=status.HTTP_404_NOT_FOUND)

class SessionStatsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HTTPSPagination

    def get(self, request, *args, **kwargs):
        try:
            # Get query parameters for filtering
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            min_score = request.GET.get('min_score', 0)

            # Start with base queryset
            sessions = Session.objects.filter(user=request.user)

            # Apply date filters if provided
            if start_date:
                sessions = sessions.filter(created__gte=start_date)
            if end_date:
                sessions = sessions.filter(created__lte=end_date)

            # Filter by minimum toxicity score if provided
            sessions = sessions.filter(session_tox_score__gte=min_score)

            # Annotate with additional metrics including player counts
            top_sessions = sessions.annotate(
                message_count=models.Count('session_chat_message'),
                flagged_message_count=models.Count(
                    'session_chat_message',
                    filter=models.Q(session_chat_message__flagged=True)
                ),
                total_players=models.Count(
                    'session_chat_message__player_id',
                    distinct=True
                ),
                toxic_players=models.Count(
                    'session_chat_message__player_id',
                    filter=models.Q(session_chat_message__flagged=True),
                    distinct=True
                )
            ).order_by('-session_tox_score')

            # Paginate results
            paginated_sessions = self.paginate_queryset(top_sessions)

            # Prepare response data
            session_data = []
            for session in paginated_sessions:
                session_data.append({
                    'session_id': session.sessionId,
                    'tox_score': session.session_tox_score,
                    'total_messages': session.message_count,
                    'flagged_messages': session.flagged_message_count,
                    'total_players': session.total_players,
                    'toxic_players': session.toxic_players,
                    'created': session.created,
                    'updated': session.updated,
                })

            return JsonResponse({
                'sessions': session_data,
                'total_sessions': sessions.count(),
            }, safe=False, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SystemStatsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get total messages and flagged messages
            total_messages = ChatMessage.objects.filter(user=request.user).count()
            total_flagged_messages = ChatMessage.objects.filter(
                user=request.user,
                flagged=True
            ).count()

            # Get total sessions and toxic sessions
            total_sessions = Session.objects.filter(user=request.user).count()
            toxic_sessions = Session.objects.filter(
                user=request.user,
                session_tox_score__gt=0
            ).count()

            # Get total players and toxic players
            total_players = Player.objects.filter(user=request.user).count()
            toxic_players = Player.objects.filter(
                user=request.user,
                player_tox_score__gt=0
            ).count()

            return JsonResponse({
                'total_messages': total_messages,
                'total_flagged_messages': total_flagged_messages,
                'total_sessions': total_sessions,
                'toxic_sessions': toxic_sessions,
                'total_players': total_players,
                'toxic_players': toxic_players,
                'flagged_message_percentage': round((total_flagged_messages / total_messages * 100) if total_messages > 0 else 0, 2),
                'toxic_session_percentage': round((toxic_sessions / total_sessions * 100) if total_sessions > 0 else 0, 2),
                'toxic_player_percentage': round((toxic_players / total_players * 100) if total_players > 0 else 0, 2)
            }, safe=False, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SessionDetailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            session_id = kwargs.get('sessionid')
            session = Session.objects.get(user=request.user, sessionId=session_id)
            
            # Get basic session stats
            session_stats = Session.objects.filter(id=session.id).annotate(
                message_count=models.Count('session_chat_message'),
                flagged_message_count=models.Count(
                    'session_chat_message',
                    filter=models.Q(session_chat_message__flagged=True)
                ),
                total_players=models.Count(
                    'session_chat_message__player',
                    distinct=True
                ),
                toxic_players=models.Count(
                    'session_chat_message__player',
                    filter=models.Q(session_chat_message__flagged=True),
                    distinct=True
                )
            ).first()

            # Get toxic messages sorted by tox_score
            toxic_messages = ChatMessage.objects.filter(
                session=session,
                flagged=True
            ).order_by('-assigned_tox_score').values(
                'message',
                'assigned_tox_score',
                'player__playerName',
                'created'
            )

            # Get top 5 toxic players in session
            toxic_players = Player.objects.filter(
                player_chat_message__session=session
            ).annotate(
                session_tox_score=models.Avg('player_chat_message__assigned_tox_score'),
                toxic_messages_count=models.Count(
                    'player_chat_message',
                    filter=models.Q(
                        player_chat_message__session=session,
                        player_chat_message__flagged=True
                    )
                )
            ).order_by('-session_tox_score')[:5].values(
                'playerName',
                'player_tox_score',
                'session_tox_score',
                'toxic_messages_count'
            )

            return JsonResponse({
                'session_id': session.sessionId,
                'tox_score': session.session_tox_score,
                'total_messages': session_stats.message_count,
                'flagged_messages': session_stats.flagged_message_count,
                'total_players': session_stats.total_players,
                'toxic_players': session_stats.toxic_players,
                'created': session.created,
                'updated': session.updated,
                'toxic_messages': list(toxic_messages),
                'top_toxic_players': list(toxic_players)
            }, safe=False, status=status.HTTP_200_OK)

        except Session.DoesNotExist:
            return JsonResponse({
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)