from django.contrib import admin
from .models import Account, Otpveification1
# Register your models here.

class AccountAdmin(admin.ModelAdmin):
    list_display = ('userName', 'email')
    search_fields = ('userName', 'email')


class AccountAdmin1(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number',)


admin.site.register(Account, AccountAdmin)
admin.site.register(Otpveification1, AccountAdmin1)
