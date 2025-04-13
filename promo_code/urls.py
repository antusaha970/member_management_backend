from django.urls import path
from promo_code.views import (
   PromoCodeCategoryView,
   PromoCodeView
)

urlpatterns = [
    path('v1/promo_codes/categories/', PromoCodeCategoryView.as_view(), name='promo_code_categories'),
    path('v1/promo_codes/', PromoCodeView.as_view(), name='promo_codes'),
    
]