from django.urls import path, include
from . import views
urlpatterns = [
    # SMTP Configurations
    path("v1/configs/", views.SetMailConfigurationAPIView.as_view(),
         name="mail_config_list_create_view"),
    path("v1/configs/<int:id>/", views.SetMailConfigurationAPIView.as_view(),
         name="mail_config_detail_view"),
    # Email Composes
    path("v1/email/composes/", views.EmailComposeView.as_view(),
         name="mail_compose_list_create_view"),
    path("v1/email/composes/<int:id>/", views.EmailComposeDetailView.as_view(),
         name="mail_compose_detail_view"),
    # Email Groups
    path("v1/email/groups/", views.EmailGroupView.as_view(),
         name="email_group_list_create_view"),
    path("v1/email/groups/<int:group_id>/",
         views.EmailGroupDetailView.as_view(), name="email_group_detail_view"),
    # Email Lists
    path("v1/email/lists/", views.EmailListView.as_view(),
         name="email_list_list_create_view"),
    path("v1/email/lists/<int:id>/", views.EmailListDetailView.as_view(),
         name="email_list_detail_view"),
    # Individual Emails
    path("v1/email/individual_emails/", views.SingleEmailView.as_view(), name="individual_email_list_create_view"),
    path("v1/email/individual_emails/<int:id>/", views.SingleEmailView.as_view(), name="individual_email_detail_view"),
    # Send Email Action (Bulk or Single)
    path("v1/emails/send/", views.EmailSendView.as_view(), name="email_send"),
]
