from django.urls import path
from . import views
urlpatterns = [
    path("v1/payment/options/", views.PaymentMethodView.as_view(),
         name="payment_options_view"),
    path("v1/payment/invoice/", views.InvoicePaymentView.as_view(),
         name="invoice_payment_view"),
    path("v1/income/particular/", views.IncomeParticularView.as_view(),
         name="income_particular_view"),
    path("v1/income/receiving_options/", views.IncomeReceivedFromView.as_view(),
         name="income_receiving_option_view"),
]
