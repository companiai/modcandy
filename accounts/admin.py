from django.contrib import admin
from accounts.models import CustomUser, LoginTimeStamps, UserAPIKey

class CustomReadOnlyAdmin(admin.ModelAdmin):

    def has_change_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(CustomUser, CustomReadOnlyAdmin)
admin.site.register(LoginTimeStamps, CustomReadOnlyAdmin)
admin.site.register(UserAPIKey, CustomReadOnlyAdmin)