from rest_framework import generics, status
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from equalizer.analyzer import PerspectiveUtil
from equalizer.util import EqualizerUtil


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

    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        perspective_util = PerspectiveUtil(debug=False)
        if data.get('text', None):
            data, error = perspective_util.simple_tox_score(text=data.get('text'))
            if error:
                return JsonResponse(
                    data,
                    safe=False,
                    status=status.HTTP_200_OK
                )
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

    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        perspective_util = PerspectiveUtil(debug=False)
        if( data.get('playerID', None) and data.get('text', None) and data.get('sessionID', None)):
            data, error = perspective_util.player_tox_score(text=data.get('text'), playerId=data.get('playerID'), sessionId=data.get('sessionID'), playerName=data.get('playerName', ''))
            if error:
                return JsonResponse(
                    data,
                    safe=False,
                    status=status.HTTP_200_OK
                )
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