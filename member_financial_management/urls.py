from django.urls import path
from . import views
urlpatterns = [
    path("v1/payment/options/", views.PaymentMethodView.as_view(),
         name="payment_options_view"),
]
