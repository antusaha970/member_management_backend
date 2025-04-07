from django.urls import path
from product.views import BrandView,ProductCategoryView

urlpatterns = [
    path('v1/products/brands/', BrandView.as_view(), name='product_brands'),
    path('v1/products/categories/', ProductCategoryView.as_view(), name='product_categories'),
    
]