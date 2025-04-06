from django.urls import path
from . import views
urlpatterns = [
    path("v1/restaurants/", views.RestaurantView.as_view(),
         name="restaurant_view"),
    path("v1/restaurants/cusines/", views.RestaurantCuisineCategoryView.as_view(),
         name="restaurant_cuisine_view"),
    path("v1/restaurants/categories/", views.RestaurantCategoryView.as_view(),
         name="restaurant_categories_view"),
    path("v1/restaurants/items/categories/", views.RestaurantItemCategoryView.as_view(),
         name="restaurant_categories_view"),
    path("v1/restaurants/items/", views.RestaurantItemView.as_view(),
         name="restaurant_items_view"),
]
