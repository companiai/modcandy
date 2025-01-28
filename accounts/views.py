from knox.views import LoginView as KnoxLoginView
from rest_framework.parsers import JSONParser
from rest_framework import permissions, generics, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_api_key.models import APIKey
from rest_framework.response import Response
from django.contrib.auth import login
from accounts.serializers import UserSerializer, UserAPIKeySerializer
from accounts.models import UserAPIKey
import ipdb

# Create your views here.

class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # LoginTimeStamps.objects.create(user=user)
        login(request, user)
        return super(LoginView, self).post(request, format=None)
    

class UserAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    

class APIKeyView(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        try:
            data = self.request.user.user_api_key
            serializer = UserAPIKeySerializer(data)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    
    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        api_key, key = APIKey.objects.create_key(name=data.get('keyname')+str(request.user.id))
        UserAPIKey.objects.create(user=request.user, keyname=data.get('keyname'), key=api_key)
        return Response(
            {
                'key': key
            },
            status=status.HTTP_200_OK
        )
    
    def delete(self, request, *args, **kwargs):
        request.user.user_api_key.key.delete()
        return Response(
            {
                'message': 'Key Deleted'
            },
            status=status.HTTP_200_OK
        )