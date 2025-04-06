from rest_framework import serializers
from .models import RestaurantCuisineCategory, RestaurantCategory


class RestaurantCuisineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCuisineCategory
        fields = ["id", "name"]


class RestaurantCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCategory
        fields = ["id", "name"]
