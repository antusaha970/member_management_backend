from rest_framework import serializers
from .models import *


class MembershipTypeSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate_name(self, value):
        upp_value = value.upper()
        is_exist = MembershipType.objects.filter(name=upp_value).exists()
        if is_exist:
            raise serializers.ValidationError(
                f'{value} already exists'
            )
        return upp_value

    def create(self, validated_data):
        name = validated_data.get('name')
        membership_type = MembershipType.objects.create(name=name)
        return membership_type


class InstituteNameSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate_name(self, value):
        is_exist = InstituteName.objects.filter(name=value).exists()
        if is_exist:
            raise serializers.ValidationError(
                f'{value} already exists'
            )
        return value

    def create(self, validated_data):
        name = validated_data.get('name')
        institute_name = InstituteName.objects.create(name=name)
        return institute_name


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = "__all__"


class MembershipStatusChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipStatusChoice
        fields = "__all__"
