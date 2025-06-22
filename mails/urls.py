from django.urls import path, include
from . import views
urlpatterns = [

    path("v1/configs/", views.SetMailConfigurationAPIView.as_view(),
         name="mail_config_view"),
    path("v1/configs/<int:id>/", views.SetMailConfigurationAPIView.as_view(),
         name="mail_config_update_view"),

    path("v1/email/composes/", views.EmailComposeView.as_view(),
         name="mail_compose_view")
]
