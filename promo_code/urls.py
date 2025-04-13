from django.urls import path
from promo_code.views import (
   PromoCodeCategoryView,
   PromoCodeDetailView
)

urlpatterns = [
    path('v1/promo_codes/categories/', PromoCodeCategoryView.as_view(), name='promo_code_categories'),
    path('v1/promo_codes/', PromoCodeDetailView.as_view(), name='promo_codes'),
    
]