from rest_framework import serializers
from .models import RestaurantCuisineCategory


class RestaurantCuisineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCuisineCategory
        fields = ["id", "name"]
