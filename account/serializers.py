from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from club.models import Club
from .models import *
import pdb

# user serializes


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ["password", "last_login",
                   "is_superuser", "groups", "user_permissions"]
        depth = 1


# Authentication serializers
class RegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    remember_me = serializers.BooleanField(default=False)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email',
                  'name', 'club', 'remember_me']
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


class AdminUserRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email',
                  'name', 'club',]
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
    remember_me = serializers.BooleanField(default=False)

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


# autherzaiton serializers


class CustomPermissionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)

    def validate_name(self, value):
        restricted_words = ["admin", "user"]
        if any(word in value.lower() for word in restricted_words):
            raise serializers.ValidationError(
                "The name cannot contain 'admin' or 'user'.")

        if PermissonModel.objects.filter(name=value.replace(' ', '_').lower()).exists():
            raise serializers.ValidationError(
                f"Permission with this name {value} already exists.")

        return value

    def create(self, validated_data):
        name = validated_data.get('name')
        permission = PermissonModel.objects.create(
            name=name.replace(' ', '_').lower())

        return permission


class CustomPermissionSerializerForView(serializers.ModelSerializer):
    class Meta:
        model = PermissonModel
        fields = "__all__"


class GroupModelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250, required=True)
    permission = serializers.PrimaryKeyRelatedField(
        queryset=PermissonModel.objects.all(), many=True, required=True)

    def validate_name(self, value):
        if self.instance:
            # if we are updating existing instance then make sure new name doesn't conflict with existing groups
            if self.instance.name != value:
                is_new_name_exist = GroupModel.objects.filter(
                    name=value).exists()
                if is_new_name_exist:
                    raise serializers.ValidationError(
                        f"{value} name already exists")

            return value
        name = value.replace(' ', '_').lower()
        if GroupModel.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                f"Group with this name {value} already exists.")

        return name

    def create(self, validated_data):
        permissions_data = validated_data.pop('permission')
        group = GroupModel.objects.create(**validated_data)
        group.permission.set(permissions_data)
        return group

    def update(self, instance, validated_data):
        group_name = validated_data.get("name")
        permissions = validated_data.get("permission")
        instance.name = group_name
        instance.permission.set(permissions)
        instance.save()
        return instance


class AssignGroupPermissionSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=True)
    group = serializers.PrimaryKeyRelatedField(
        queryset=GroupModel.objects.all(), many=True, required=True)

    def create(self, validated_data):
        groups = validated_data.pop('group')

        assign_group_permission = AssignGroupPermission.objects.create(
            **validated_data)

        assign_group_permission.group.set(groups)

        return assign_group_permission


class GroupSerializerForViewAllGroups(serializers.ModelSerializer):
    class Meta:
        model = GroupModel
        fields = "__all__"
        depth = 1


class DeleteUserFromGroupSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=True)
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=GroupModel.objects.all(), required=True)

    def validate_group_id(self, value):
        user = self.initial_data.get('user_id')
        user = get_user_model().objects.get(pk=user)
        # Check if the user is in the group
        user_in_group = AssignGroupPermission.objects.filter(
            user=user, group=value
        ).exists()
        if not user_in_group:
            raise serializers.ValidationError("The user is not in this group.")

        return value
