from django.db import models
from member.models import MembershipType
import product


class ProductBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class ProductCategory(ProductBaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Brand(ProductBaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(ProductBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0)
    quantity_in_stock = models.PositiveIntegerField()
    sku = models.CharField(max_length=50, unique=True)
    # foreign key relation
    category = models.ForeignKey(
        ProductCategory, on_delete=models.RESTRICT, related_name="products_category")
    brand = models.ForeignKey(Brand, on_delete=models.RESTRICT,
                              null=True, blank=True, related_name="products_brand")
    class Meta:
        unique_together = ('name', 'category')


    def __str__(self):
        return self.name


class ProductMedia(ProductBaseModel):
    image = models.ImageField(upload_to='product_photos/')
    # foreignkey relations
    product = models.ForeignKey(
        Product, on_delete=models.RESTRICT, related_name="product_media")

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductPrice(ProductBaseModel):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Foreignkey relations
    product = models.ForeignKey(
        Product, on_delete=models.RESTRICT, related_name="product_prices")
    membership_type = models.ForeignKey(
        MembershipType, on_delete=models.RESTRICT, related_name="product_prices_membership_type")
    
    class Meta:
        unique_together = ('product', 'membership_type')
    def __str__(self):
        return f"Price {self.price} for {self.product.name}"
