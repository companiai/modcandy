from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_api_key.models import APIKey
# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    

class UserAPIKey(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_api_key')
    key = models.OneToOneField(APIKey, on_delete=models.CASCADE, related_name='user_rest_key')
    keyname = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key.prefix
    
    @property
    def key_prefix(self):
        return self.key.prefix