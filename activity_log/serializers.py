

from rest_framework import serializers
from .models import ActivityLog


class AdminActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'timestamp', 'ip_address', 'location', 'user_agent',
                  'request_method', 'referrer_url', 'device', 'path', 'verb',
                  'severity_level', 'description']


class NormalUserActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'timestamp', 'ip_address',
                  'location', 'verb', 'description', 'path']


class AllUserActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'timestamp', 'ip_address', 'location', 'user_agent',
                  'request_method', 'referrer_url', 'device', 'path', 'verb',
                  'severity_level', 'description']
