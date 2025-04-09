
from rest_framework import serializers
from .models import Facility,FacilityUseFee,FACILITY_STATUS_CHOICES,USAGES_ROLES_CHOICES
from core.models import MembershipType
from member.models import Member

import pdb


class FacilitySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    usages_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    usages_roles = serializers.ChoiceField(choices=USAGES_ROLES_CHOICES, default='member')
    operating_hours = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(choices=FACILITY_STATUS_CHOICES, default='open')
    capacity = serializers.IntegerField(min_value=1)

    def validate_name(self, value):
        if Facility.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"A facility with this name {value} already exists.")
        return value
    def validate_usages_fee(self, value):
        if value <= 0:
            raise serializers.ValidationError("Usages fee must be greater than 0.")
        return value
    def validate_operating_hours(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Operating hours must be 1 or more")
        return value
    
    def create(self, validated_data):
        """
        Create a new Facility instance.
        """
        facility = Facility.objects.create(**validated_data)
        return facility
    
class FacilityViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"
              
    
    
    