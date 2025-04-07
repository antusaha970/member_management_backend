
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
        


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    quantity_in_stock = serializers.IntegerField()
    sku = serializers.CharField(max_length=50)
    category = serializers.IntegerField()
    brand = serializers.IntegerField(required=False, allow_null=True)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_discount_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount rate must be between 0 and 100.")
        return value

    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value

    def validate_category(self, value):
        try:
            category_instance = ProductCategory.objects.get(pk=value)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError("Category does not exist.")
        return category_instance

    def validate_brand(self, value):
        
        try:
            brand_instance = Brand.objects.get(pk=value)
        except Brand.DoesNotExist:
            raise serializers.ValidationError("Brand does not exist.")
        return brand_instance


    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        return product

class ProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        depth = 1

class ProductMediaSerializer(serializers.Serializer):
    image = serializers.ImageField()
    product = serializers.IntegerField() 

    def validate_product(self, value):
        try:
            product_instance = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        return product_instance


    def create(self, validated_data):
        media =  ProductMedia.objects.create(**validated_data) 
        return media
    
class ProductMediaViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = "__all__"
        depth = 1