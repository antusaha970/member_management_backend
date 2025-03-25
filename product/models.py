from django.db import models
from member.models import MembershipType


class ProductCategory(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    # forign key reletion
    category = models.ForeignKey(ProductCategory, on_delete=models.RESTRICT)
    brand = models.ForeignKey(Brand, on_delete=models.RESTRICT,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    quantity_in_stock = models.PositiveIntegerField()
    sku = models.CharField(max_length=50, unique=True)
    # record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductMedia(models.Model):
    image = models.ImageField(upload_to='product_photos/')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.RESTRICT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # record keeping
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Price {self.price} for {self.product.name}"
   
    
    
    
    