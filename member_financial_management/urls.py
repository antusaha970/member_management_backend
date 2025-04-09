from django.urls import path
from . import views
urlpatterns = [
    path("v1/payment/options/", views.PaymentMethodView.as_view(),
         name="payment_options_view"),
    path("v1/payment/invoice/", views.InvoicePaymentView.as_view(),
         name="invoice_payment_view"),
    path("v1/income/particular/", views.IncomeParticularView.as_view(),
         name="income_particular_view"),
    path("v1/income/", views.IncomeView.as_view(),
         name="income_view"),
    path("v1/income/<int:id>/", views.IncomeSpecificView.as_view(),
         name="income_specific_view"),
    path("v1/income/receiving_options/", views.IncomeReceivedFromView.as_view(),
         name="income_receiving_option_view"),
    path("v1/invoices/", views.InvoiceShowView.as_view(),
         name="invoice_show_view"),
    path("v1/invoices/<int:id>/", views.InvoiceSpecificView.as_view(),
         name="invoice_specific_view"),
    path("v1/sales/", views.SalesView.as_view(),
         name="sales_view"),
    path("v1/sales/<int:id>/", views.SalesSpecificView.as_view(),
         name="sales_specific_view"),
    path("v1/transactions/", views.TransactionView.as_view(),
         name="transaction_view"),
    path("v1/transactions/<int:id>/", views.TransactionSpecificView.as_view(),
         name="transaction_specific_view"),

]
