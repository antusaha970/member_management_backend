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
        queryset=PromoCodeCategory.objects.all(), many=True)

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
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        percentage = attrs.get('percentage')
        amount = attrs.get('amount')
        remaining_limit = attrs.get('remaining_limit')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be greater than end date.")

        if percentage is not None and 'amount' in self.initial_data:
            raise serializers.ValidationError("Cannot provide both percentage and amount.")
        if amount is not None and 'percentage' in self.initial_data:
            raise serializers.ValidationError("Cannot provide both amount and percentage.")

        if percentage is None and amount is None:
            raise serializers.ValidationError("Either percentage or amount must be provided.")
        
        if 'remaining_limit' in self.initial_data:
            raise serializers.ValidationError("Remaining limit cannot be set manually.")

        return attrs


    def create(self, validated_data):
        category = validated_data.pop("category")
        promo_code = PromoCode.objects.create(**validated_data)
        promo_code.category.set(category)
        return promo_code


class PromoCodeDetailViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = "__all__"
        depth = 1


class AppliedPromoCodeSerializer(serializers.ModelSerializer):

    promo_code = serializers.SerializerMethodField()
    used_by = serializers.SerializerMethodField()

    class Meta:
        model = AppliedPromoCode
        fields = "__all__"

    def get_promo_code(self, obj):
        return obj.promo_code.promo_code

    def get_used_by(self, obj):
        return obj.used_by.member_ID
