from rest_framework import serializers
from .models import *


class SMTPConfigurationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    provider = serializers.CharField(max_length=50)
    host = serializers.CharField(max_length=255, required=False)
    port = serializers.IntegerField(required=False)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    use_tls = serializers.BooleanField(required=False)
    use_ssl = serializers.BooleanField(required=False)
    aws_access_key_id = serializers.CharField(max_length=255, required=False)
    aws_secret_access_key = serializers.CharField(
        max_length=255, required=False)
    aws_region = serializers.CharField(max_length=50, required=False)
    ses_configuration_set = serializers.CharField(
        max_length=255, required=False)
    iam_role_arn = serializers.CharField(max_length=255, required=False)
    enable_tracking = serializers.BooleanField(required=False)

    def validate(self, attrs):
        provider = attrs.get('provider')
        if provider == 'gmail':
            if not attrs.get('username') or not attrs.get('password'):
                raise serializers.ValidationError(
                    "Username and password are required for 'gmail' provider.")
        else:
            raise serializers.ValidationError(
                "Currently not accepting any other provider.")

        return attrs

    def create(self, validated_data):
        provider = validated_data.get("provider")
        username = validated_data.get("username")
        password = validated_data.get("password")
        user = validated_data.pop('user')

        obj = SMTPConfiguration.objects.create(
            provider=provider, username=username, password=password, user=user)
        return obj
