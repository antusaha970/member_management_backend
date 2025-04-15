from rest_framework import serializers
from .models import PromoCodeCategory, PromoCode, AppliedPromoCode
from core.models import MembershipType
from member.models import Member
import pdb


class PromoCodeCategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

    def validate_name(self, value):
        # Check if the name already exists in the database
        to_lower = value.lower().replace(" ", "_")
        if PromoCodeCategory.objects.filter(name=to_lower).exists():
            raise serializers.ValidationError(
                f"Promo Code Category with this name {to_lower} already exists.")
        return to_lower

    def create(self, validated_data):
        category = PromoCodeCategory.objects.create(**validated_data)
        return category


class PromoCodeCategoryViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCodeCategory
        fields = "__all__"


class PromoCodeSerializer(serializers.Serializer):
    promo_code = serializers.CharField(max_length=100)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True)
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True)
    limit = serializers.IntegerField()
    remaining_limit = serializers.IntegerField(required=False, default=0)
    description = serializers.CharField()
    # foreignkey relations
    category = serializers.PrimaryKeyRelatedField(
        queryset=PromoCodeCategory.objects.all())

    def validate_promo_code(self, value):
        # Check if the promo code already exists in the database
        if PromoCode.objects.filter(promo_code=value).exists():
            raise serializers.ValidationError(
                f"Promo code {value} already exists.")
        return value

    def validate_limit(self, value):
        # Check if the limit is greater than 0
        if value <= 0:
            raise serializers.ValidationError("Limit must be greater than 0.")
        return value

    def validate_amount(self, value):
        # Check if the amount is greater than 0
        if value != None and value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_percentage(self, value):

        if value != None and (value < 0 or value > 100):
            raise serializers.ValidationError(
                "Percentage must be between 0 and 100.")
        return value

    def validate(self, attrs):

        # check start date and end date
        if attrs.get('start_date') > attrs.get('end_date'):
            raise serializers.ValidationError(
                "Start date cannot be greater than end date.")

        # check if both percentage and amount are provided
        if attrs.get('percentage') is not None and attrs.get('amount') is not None:
            raise serializers.ValidationError(
                "Either percentage or amount should be provided, but not both")

        return attrs

    def create(self, validated_data):
        promo_code = PromoCode.objects.create(**validated_data)
        return promo_code


class PromoCodeDetailViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = "__all__"
        depth = 1
