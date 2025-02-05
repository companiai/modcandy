from django.contrib.auth import login
from django.utils import timezone
from knox.views import LoginView as KnoxLoginView
from knox.models import AuthToken
from rest_framework.parsers import JSONParser
from rest_framework import permissions, generics, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_api_key.models import APIKey
from rest_framework.response import Response


from accounts.serializers import UserSerializer, UserAPIKeySerializer, RegisterSerializer, UserCreditUsageSerializer
from accounts.models import UserAPIKey, LoginTimeStamps, UserCreditUsage
from accounts.utils import send_slack_notification
import ipdb

# Create your views here.

class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        LoginTimeStamps.objects.update_or_create(user=user, defaults={'login_time': timezone.now()})
        login(request, user)
        return super(LoginView, self).post(request, format=None)
    

class UserAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
# Register API
# TODO: Send Email Verification Code
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            # send_slack_notification(' New User Signup: {}'.format(user.username))
            # subject = 'Welcome to Modcandy! Let's Get Started.'
            # send_template_message(
            #     template_name='Welcome Mail',
            #     subject=subject,
            #     to=user.email,
            #     variable_data={"company_name": user.email},
            # )

            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1]
            })
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    

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
    
class UserCreditUsageView(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserCreditUsageSerializer

    def get(self, request, *args, **kwargs):
        data, _ = UserCreditUsage.objects.get_or_create(user=request.user)
        serializer = UserCreditUsageSerializer(data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )