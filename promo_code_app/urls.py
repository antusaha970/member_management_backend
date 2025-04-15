
from django.urls import path
from promo_code_app.views import (
    PromoCodeCategoryView,
    PromoCodeView,
    AppliedPromoCodeView
)

urlpatterns = [
    path('v1/promo_codes/categories/', PromoCodeCategoryView.as_view(),
         name='promo_code_categories'),
    path('v1/promo_codes/', PromoCodeView.as_view(), name='promo_codes'),
    path('v1/applied_promo_codes/', AppliedPromoCodeView.as_view(),
         name='applied_promo_code_view'),
]
