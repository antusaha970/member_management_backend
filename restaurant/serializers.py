from rest_framework import serializers
from .models import RestaurantCuisineCategory, RestaurantCategory, Restaurant, RestaurantItemCategory, RestaurantItem, RestaurantItemMedia
from member.models import Member
from promo_code_app.models import PromoCode
import pdb


class RestaurantCuisineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCuisineCategory
        fields = ["id", "name"]


class RestaurantCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCategory
        fields = ["id", "name"]


class RestaurantSerializer(serializers.Serializer):
    STATUS_CHOICES = [
        ('open', 'open'),
        ('closed', 'closed'),
    ]
    name = serializers.CharField(max_length=300)
    description = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField(max_length=250)
    state = serializers.CharField(max_length=250)
    postal_code = serializers.CharField(max_length=250)
    phone = serializers.CharField(max_length=14)
    operating_hours = serializers.IntegerField()
    capacity = serializers.IntegerField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    opening_time = serializers.TimeField()
    closing_time = serializers.TimeField()
    booking_fees_per_seat = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    cuisine_type = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantCuisineCategory.objects.all())
    restaurant_type = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantCategory.objects.all())

    def validate_name(self, value):
        if Restaurant.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                f"Restaurant with name {value} already exists")
        return value

    def create(self, validated_data):
        instance = Restaurant.objects.create(**validated_data)
        return instance


class RestaurantViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = "__all__"
        depth = 1


class RestaurantItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantItemCategory
        fields = "__all__"


class RestaurantItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=300)
    description = serializers.CharField(max_length=300)
    availability = serializers.BooleanField()
    unit = serializers.CharField(max_length=100)
    unit_cost = serializers.DecimalField(max_digits=6, decimal_places=2)
    selling_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    category = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantItemCategory.objects.filter(is_active=True))
    restaurant = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.filter(is_active=True))

    def validate_name(self, value):
        if RestaurantItem.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"{value} already exists")
        return value

    def create(self, validated_data):
        instance = RestaurantItem.objects.create(**validated_data)
        return instance


class ItemMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantItemMedia
        fields = ['image']


class RestaurantItemForViewSerializer(serializers.ModelSerializer):
    restaurant = serializers.CharField()
    category = serializers.CharField()
    item_media = ItemMediaSerializer(many=True, read_only=True)

    class Meta:
        model = RestaurantItem
        fields = "__all__"
        depth = 1


class RestaurantItemMediaSerializer(serializers.Serializer):
    image = serializers.ImageField()
    item = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantItem.objects.all())

    def create(self, validated_data):
        instance = RestaurantItemMedia.objects.create(**validated_data)
        return instance


class RestaurantItemMediaForViewSerializer(serializers.Serializer):
    image = serializers.ImageField()


class RestaurantSingleItemForBuySerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantItem.objects.filter(is_active=True))
    quantity = serializers.IntegerField()


class RestaurantItemBuySerializer(serializers.Serializer):
    restaurant_items = serializers.ListSerializer(
        child=RestaurantSingleItemForBuySerializer(), allow_empty=False)
    member_ID = serializers.CharField()
    restaurant = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.filter(is_active=True))
    promo_code = serializers.CharField(required=False, default=None)

    def validate_member_ID(self, value):
        if not Member.objects.filter(member_ID=value).exists():
            raise serializers.ValidationError(f"{value} is not a member")
        return value

    def validate_promo_code(self, value):
        if value == None:
            return value
        try:
            promo_code = PromoCode.objects.get(promo_code=value)
            is_in_restaurant_category = promo_code.category.filter(
                name__iexact="restaurant").exists()
            if not promo_code.is_promo_code_valid():
                raise serializers.ValidationError(
                    "This promo code is expired or not valid any more.")
            else:
                if is_in_restaurant_category:
                    return promo_code
                else:
                    raise serializers.ValidationError(
                        "This is not a restaurant category promo code.")
        except PromoCode.DoesNotExist as e:
            raise serializers.ValidationError(
                "This is not a valid promo code.")
