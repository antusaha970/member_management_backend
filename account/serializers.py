from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from club.models import Club
import pdb
from django.contrib.auth.models import Group,Permission
from .models import PermissonModel,GroupModel,AssignGroupPermission
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



class CustomPermissionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)

    def validate_name(self, value):
        restricted_words = ["admin", "user"]
        if any(word in value.lower() for word in restricted_words):
            raise serializers.ValidationError("The name cannot contain 'admin' or 'user'.")

        if PermissonModel.objects.filter(name=value.replace(' ','_').lower()).exists():
            raise serializers.ValidationError(f"Permission with this name {value} already exists.")

        return value
    
    def create(self, validated_data):
        name = validated_data.get('name')
        permission = PermissonModel.objects.create(name=name.replace(' ','_').lower())
            
        return permission

class CustomPermissionSerializerForView(serializers.ModelSerializer):
    class Meta:
        model=PermissonModel
        fields="__all__"   

class GroupModelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250, required=True)
    permission = serializers.PrimaryKeyRelatedField(queryset=PermissonModel.objects.all(), many=True,required=True)

    def validate_name(self,value):
        name=value.replace(' ','_').lower()
        if  GroupModel.objects.filter(name=name).exists():
            raise serializers.ValidationError(f"Group with this name {value} already exists.")

        return name
    
    def create(self, validated_data):
        permissions_data = validated_data.pop('permission')
        group = GroupModel.objects.create(**validated_data)
        group.permission.set(permissions_data)
        return group

    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
        
    #     if 'permission' in validated_data:
    #         permissions_data = validated_data.pop('permission')
    #         instance.permission.set(permissions_data)
        
    #     instance.save()
    #     return instance

 
class AssignGroupPermissionSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), many=True,required=True)
    group = serializers.PrimaryKeyRelatedField(queryset=GroupModel.objects.all(), many=True,required=True)
    permission = serializers.PrimaryKeyRelatedField(queryset=PermissonModel.objects.all(), many=True,required=True)

    
    def create(self, validated_data):
        user=self.validated_data.get("user")
        group=self.validated_data.get("group")
        permission=self.validated_data.get("permission")
        
        assign_group_permission=AssignGroupPermission.objects.create(**validated_data)
        assign_group_permission.user.set(user=user)
        return 