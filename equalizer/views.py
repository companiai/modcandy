from rest_framework import generics, status, permissions
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from equalizer.analyzer import PerspectiveUtil
from equalizer.util import EqualizerUtil
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from equalizer.models import ToxicityIncident
from equalizer.serializers import IncidentSerializer
from django_filters import rest_framework as filters
from datetime import datetime

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

class IncidentView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IncidentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ToxicityIncidentFilter

    def get_queryset(self):
        return ToxicityIncident.objects.filter(user=self.request.user)