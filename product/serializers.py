
from rest_framework import serializers
from .models import Brand,ProductPrice,Product,ProductCategory,ProductMedia
from core.models import MembershipType
from member.models import Member
import pdb

class BrandSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    
    def validate_name(self, value):
        if Brand.objects.filter(name=value).exists():
            raise serializers.ValidationError("Brand with this name already exists.")
        return value
    
    def create(self, validated_data):
        brand=Brand.objects.create(**validated_data)
        return brand
    
class BrandViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

class ProductCategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    
    def validate_name(self, value):
        if ProductCategory.objects.filter(name=value).exists():
            raise serializers.ValidationError("Product Category with this name already exists.")
        return value
    
    def create(self, validated_data):
        category=ProductCategory.objects.create(**validated_data)
        return category
    
class ProductCategoryViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"