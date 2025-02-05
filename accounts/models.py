from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_api_key.models import APIKey
# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    

class LoginTimeStamps(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_login_record')
    login_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.user.username
    

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
    
class UserCreditUsage(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_credit')
    credit_used = models.IntegerField(default=0)
    credit_remaining = models.IntegerField(default=1000)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username
    
    @property
    def username(self):
        return self.user.username
    
    
    def update_credit_usage(self, amount):
        self.credit_used += amount
        self.credit_remaining -= amount
        self.save()
