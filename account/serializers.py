from rest_framework import serializers
from .models import Account


class AccountSerilizer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['name', 'userName', 'number', 'email', 'profile_pic']