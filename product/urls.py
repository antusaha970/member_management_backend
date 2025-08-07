from django.urls import path
from product.views import (
    BrandView,ProductCategoryView,ProductView,
    ProductMediaView,ProductPriceView,ProductDetailView,
    ProductBuyView,ProductCategoryDetailView,ProductBrandDetailView
)

urlpatterns = [
    path('v1/products/brands/', BrandView.as_view(), name='product_brands'),
    path('v1/products/brands/<int:pk>/', ProductBrandDetailView.as_view(), name='product_brands'),
    path('v1/products/categories/', ProductCategoryView.as_view(), name='product_categories'),
    path('v1/products/categories/<int:pk>/', ProductCategoryDetailView.as_view(), name='product_categories_details'),
    path('v1/products/', ProductView.as_view(), name='products'),
    path('v1/products/<int:product_id>/', ProductDetailView.as_view(), name='product_details'),
    path('v1/products/buy/', ProductBuyView.as_view(), name='product_buy'),
    path('v1/products/media/', ProductMediaView.as_view(), name='products_media'),
    path('v1/products/prices/', ProductPriceView.as_view(), name='products_prices'),
    
]