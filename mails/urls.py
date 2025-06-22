from django.urls import path, include
from . import views
urlpatterns = [
    
    path("v1/configs/", views.SetMailConfigurationAPIView.as_view(), name="mail_config_view"),
    path("v1/email/groups/", views.EmailGroupView.as_view(), name="email_group_view"),
    path("v1/email/groups/<int:group_id>/", views.EmailGroupView.as_view(), name="email_group_view"),
    path("v1/email/groups/<int:group_id>/", views.EmailGroupDetailView.as_view(), name="email_group_detail_view"),

]
