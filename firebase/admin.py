from django.contrib import admin
from .models import devicetoken, notificationMessage
# Register your models here.
class FirebaseAdmin(admin.ModelAdmin):
    list_display = ('userName', 'fcm_token')
    search_fields = ('userName', 'fcm_token')


admin.site.register(devicetoken, FirebaseAdmin)


class FirebaseAdmin1(admin.ModelAdmin):
    list_display = ('userName',)
    search_fields = ('userName',)


admin.site.register(notificationMessage, FirebaseAdmin1)
