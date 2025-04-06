from django.db import models


class RestaurantBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class RestaurantCuisineCategory(RestaurantBaseModel):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.name


class RestaurantCategory(RestaurantBaseModel):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.name


class Restaurant(RestaurantBaseModel):
    STATUS_CHOICES = [
        ('open', 'open'),
        ('closed', 'closed'),
    ]
    name = models.CharField(max_length=300, unique=True)
    description = models.TextField(blank=True, default="")
    address = models.TextField(blank=True, default="")
    city = models.CharField(max_length=250, blank=True, default="")
    state = models.CharField(max_length=250, blank=True, default="")
    postal_code = models.CharField(max_length=250, blank=True, default="")
    phone = models.CharField(max_length=14, blank=True, default="")
    operating_hours = models.IntegerField(default=12)
    capacity = models.IntegerField(default=50)
    status = models.CharField(
        max_length=6, choices=STATUS_CHOICES, default="open")
    opening_time = models.TimeField(blank=True, null=True, default=None)
    closing_time = models.TimeField(blank=True, null=True, default=None)
    booking_fees_per_seat = models.DecimalField(
        blank=True, null=True, default=None, decimal_places=2, max_digits=10)

    # relations
    cuisine_type = models.ForeignKey(
        RestaurantCuisineCategory, on_delete=models.PROTECT, related_name="restaurant_cuisine")
    restaurant_type = models.ForeignKey(
        RestaurantCategory, on_delete=models.PROTECT, related_name="restaurant_category")

    def __str__(self):
        return self.name


class RestaurantItemCategory(RestaurantBaseModel):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.name


class RestaurantItem(RestaurantBaseModel):
    name = models.CharField(max_length=300, unique=True)
    description = models.TextField(blank=True, default="")
    availability = models.BooleanField(default=True, db_index=True)
    unit = models.CharField(max_length=100)
    unit_cost = models.DecimalField(max_digits=6, decimal_places=2)
    selling_price = models.DecimalField(max_digits=6, decimal_places=2)

    # relations
    category = models.ForeignKey(
        RestaurantItemCategory, on_delete=models.PROTECT, related_name="item_category")
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.PROTECT, related_name="restaurant_item_restaurant")

    def __str__(self):
        return self.name


class RestaurantItemMedia(RestaurantBaseModel):
    image = models.ImageField(upload_to="restaurant/items/")
    item = models.ForeignKey(
        RestaurantItem, on_delete=models.CASCADE, related_name="item_media")

    def __str__(self):
        return self.item.name
