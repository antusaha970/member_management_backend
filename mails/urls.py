from django.urls import path, include
from . import views
urlpatterns = [

    path("v1/configs/", views.SetMailConfigurationAPIView.as_view(),
         name="mail_config_view"),
    path("v1/email/groups/", views.EmailGroupView.as_view(),
         name="email_group_view"),
    path("v1/email/groups/<int:group_id>/",
         views.EmailGroupDetailView.as_view(), name="email_group_detail_view"),
    path("v1/configs/<int:id>/", views.SetMailConfigurationAPIView.as_view(),
         name="mail_config_update_view"),
    path("v1/email/composes/", views.EmailComposeView.as_view(),
         name="mail_compose_view"),
    path("v1/email/lists/", views.EmailListView.as_view(),
         name="email_list_view"),
]
