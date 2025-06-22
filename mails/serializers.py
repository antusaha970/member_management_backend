from rest_framework import serializers
from .models import *


class SMTPConfigurationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    provider = serializers.CharField(max_length=50)
    host = serializers.CharField(max_length=255)
    port = serializers.IntegerField()
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    use_tls = serializers.BooleanField()
    use_ssl = serializers.BooleanField()
    aws_access_key_id = serializers.CharField(max_length=255)
    aws_secret_access_key = serializers.CharField(max_length=255)
    aws_region = serializers.CharField(max_length=50)
    ses_configuration_set = serializers.CharField(max_length=255)
    iam_role_arn = serializers.CharField(max_length=255)
    enable_tracking = serializers.BooleanField()

    def validate(self, attrs):
        provider = attrs.get('provider')
        if provider == 'gmail':
            if not attrs.get('username') or not attrs.get('password'):
                raise serializers.ValidationError(
                    "Username and password are required for 'gmail' provider.")
