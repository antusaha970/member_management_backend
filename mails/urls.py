from django.urls import path, include
from . import views
urlpatterns = [

    path("v1/configs/", views.SetMailConfigurationAPIView.as_view(),
         name="mail_config_view")
]
