
from rest_framework import serializers
from .models import Brand,ProductPrice,Product,ProductCategory,ProductMedia
from core.models import MembershipType
from member.models import Member
from promo_code_app.models import PromoCode
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
        depth = 2
        
class ProductPriceSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    membership_type = serializers.CharField()
    product = serializers.IntegerField()

    def validate_price(self, value):

        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_membership_type(self, value):
        try:
            membership_type_instance = MembershipType.objects.get(pk=value)
        except MembershipType.DoesNotExist:
            raise serializers.ValidationError("Membership type does not exist.")
        return membership_type_instance

    def validate_product(self, value):
        try:
            product_instance = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        return product_instance

    def create(self, validated_data):
        product_price = ProductPrice.objects.create(**validated_data)
        return product_price
        
    
class ProductPriceViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = "__all__"
        depth = 2
    
    
class ProductItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset = Product.objects.filter(is_active = True))
    quantity=serializers.IntegerField(min_value=1)
    
        
class ProductBuySerializer(serializers.Serializer):
    product_items = serializers.ListSerializer(child=ProductItemSerializer(),allow_empty=False)
    member_ID = serializers.CharField()
    promo_code = serializers.CharField(required=False, default=None)

    
    def validate_member_ID(self, value):
        if not Member.objects.filter(member_ID=value).exists():
            raise serializers.ValidationError(f"{value} is not a member")
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

        if not promo_code.category.filter(name__iexact="product").exists():
            raise serializers.ValidationError("This is not an product category promo code.")

        return promo_code