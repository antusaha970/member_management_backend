
from rest_framework import serializers
from .models import Facility,FacilityUseFee,FACILITY_STATUS_CHOICES,USAGES_ROLES_CHOICES
from core.models import MembershipType
from member.models import Member
from promo_code_app.models import PromoCode
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
      
class FacilityUseFeeSerializer(serializers.Serializer):
    fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    facility = serializers.PrimaryKeyRelatedField(queryset=Facility.objects.all())
    membership_type = serializers.PrimaryKeyRelatedField(queryset=MembershipType.objects.all())

    def validate_fee(self, value):
        if value <= 0:
            raise serializers.ValidationError("Fee must be greater than 0.")
        return value
    
    def validate(self, data):
        """
        Ensure that the facility and membership type are not already linked.
        """
        if FacilityUseFee.objects.filter(facility=data['facility'], membership_type=data['membership_type']).exists():
            raise serializers.ValidationError(f"This facility {data['facility']}  and membership type {data['membership_type']} combination already exists.")
        return data

    def create(self, validated_data):
        """
        Create a new FacilityUseFee instance.
        """
        facility_use_fee = FacilityUseFee.objects.create(**validated_data)
        return facility_use_fee
    
class FacilityUseFeeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityUseFee
        fields = "__all__"
        depth = 1

class FacilityBuySerializer(serializers.Serializer):
    member_ID = serializers.CharField(max_length=255)
    facility = serializers.PrimaryKeyRelatedField(queryset=Facility.objects.all())
    promo_code = serializers.CharField(required=False, default=None)

    
    def validate_member_ID(self, value):
        if not Member.objects.filter(member_ID=value).exists():
            raise serializers.ValidationError("Member ID does not exist.")
        return value
    def validate_promo_code(self, value):
        if not value:
            return value
        try:
            promo_code = PromoCode.objects.get(promo_code=value)
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError("This is not a valid promo code.")

        if not promo_code.is_promo_code_valid():
            raise serializers.ValidationError("This promo code is expired or not valid any more.")

        if not promo_code.category.filter(name__iexact="facility").exists():
            raise serializers.ValidationError("This is not a facility category promo code.")

        return promo_code

            
    
class FacilityDetailUseFeeSerializer(serializers.ModelSerializer):
    membership_type = serializers.StringRelatedField()

    class Meta:
        model = FacilityUseFee
        fields = ['id', 'fee', 'membership_type']

class SpecificFacilityDetailSerializer(serializers.ModelSerializer):
    facility_use_fees = FacilityDetailUseFeeSerializer(many=True)

    class Meta:
        model = Facility
        fields = [
            'id',
            'name',
            'description',
            'usages_fee',
            'usages_roles',
            'operating_hours',
            'status',
            'capacity',
            'facility_use_fees'
        ]