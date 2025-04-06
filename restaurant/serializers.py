from rest_framework import serializers
from .models import RestaurantCuisineCategory, RestaurantCategory, Restaurant


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
