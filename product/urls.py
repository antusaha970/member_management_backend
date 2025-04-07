from django.urls import path
from product.views import BrandView,ProductCategoryView,ProductView,ProductMediaView

urlpatterns = [
    path('v1/products/brands/', BrandView.as_view(), name='product_brands'),
    path('v1/products/categories/', ProductCategoryView.as_view(), name='product_categories'),
    path('v1/products/', ProductView.as_view(), name='products'),
    path('v1/products/media/', ProductMediaView.as_view(), name='products_media'),
    
]