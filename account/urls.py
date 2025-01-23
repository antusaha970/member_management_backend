from django.urls import path
from . import views
urlpatterns = [
    path('v1/register/', views.AccountRegistrationView.as_view(),
         name="account_registration"),
]
