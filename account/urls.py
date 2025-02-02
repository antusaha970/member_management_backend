from django.urls import path
from . import views
urlpatterns = [
    path('v1/register/', views.AccountRegistrationView.as_view(),
         name="account_registration"),
    path('v1/login/', views.AccountLoginView.as_view(),
         name="account_login"),
    path('v1/forget_password/', views.ForgetPasswordView.as_view(),
         name="account_forget_password"),
    path('v1/reset_password/', views.ResetPasswordView.as_view(),
         name="account_reset_password"),
    path('v1/verify_otp/', views.VerifyOtpView.as_view(), name="verify_otp"),
    path('v1/authorization/custom_permission_name/',
         views.CustomPermissionView.as_view(), name="custom_permission_name"),
    path('v1/authorization/group_permissions/',
         views.GroupPermissionView.as_view(), name="group_permissions"),
    path('v1/assign_group/', views.AssignGroupPermissionView.as_view(),
         name="assign_group"),
]
