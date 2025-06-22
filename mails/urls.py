from django.urls import path, include
from . import views
urlpatterns = [

    path("v1/configs/", views.SetMailConfigurationAPIView.as_view(), name="mail_config_view"),
    path("v1/email/groups/", views.EmailGroupView.as_view(), name="email_group_view"),
    
]
