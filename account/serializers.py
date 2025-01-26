from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from club.models import Club
import pdb


class RegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email', 'name', 'club']
        extra_kwargs = {
            "name": {
                "required": True,
            },
            "email": {
                "required": True,
            },
            "username": {
                "required": True,
            },
            "password": {
                "required": True,
            },
            "club": {
                "required": True,
            }
        }

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        is_same_email_exists = get_user_model().objects.filter(
            email=email).exists()
        if is_same_email_exists:
            raise serializers.ValidationError({
                'email': f"{email} already exists",
            })
        if len(password) < 6:
            raise serializers.ValidationError({
                'password': f"Password must be at least 6 character. Current length {len(password)}"
            })

        return super().validate(attrs)

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        password = validated_data.get('password')
        name = validated_data.get('name')
        club = validated_data.get('club')

        user = get_user_model().objects.create_user(
            username=username, password=password, email=email, first_name=name, club=club)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = get_user_model().objects.filter(
            username=username).exists()

        if not user:
            raise serializers.ValidationError({
                'username': f"user {username} doesn't exist"
            })

        else:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError({
                    'password': f"password didn't matched"
                })

        return super().validate(attrs)


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        is_user_exist_with_email = get_user_model().objects.filter(
            email=email).exists()
        if not is_user_exist_with_email:
            raise serializers.ValidationError({
                'email': f"No user exist with {email}"
            })
        return super().validate(attrs)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        is_user_exist = get_user_model().objects.filter(
            email=email).exists()
        if not is_user_exist:
            raise serializers.ValidationError({
                'email': f"No user exist with {email}"
            })
        if len(password) < 6:
            raise serializers.ValidationError({
                'password': "Password must be 6 character long"
            })
        return super().validate(attrs)


class VerifyOtpSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    email = serializers.EmailField()
