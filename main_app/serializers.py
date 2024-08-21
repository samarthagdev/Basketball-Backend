from rest_framework import serializers
from .models import Players, Match


class PlayerSerializer(serializers.ModelSerializer):
    dob = serializers.DateTimeField(format="%d-%m-%y")

    class Meta:
        model = Players
        fields = ['userName', 'address', 'gender', 'name', 'pic', 'height', 'weight', 'dob', 'teams', 'points', 'assist', 'block',
                  'steal', 'totalMatch', 'rebound']


class MatchSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%d-%m-%y")

    class Meta:
        model = Match
        fields = ['date', 'match_id', 'match_between', 'match_venue']
