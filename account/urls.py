from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('v1/register/', views.AccountRegistrationView.as_view(),
         name="account_registration"),
    path('v1/login/', views.AccountLoginLogoutView.as_view(),
         name="account_login"),
    path('v1/token/refresh/', views.CustomTokenRefreshView.as_view(),
         name="token_refresh"),
    path('v1/logout/', views.AccountLoginLogoutView.as_view(),
         name="account_logout"),
    path('v1/forget_password/', views.ForgetPasswordView.as_view(),
         name="account_forget_password"),
    path('v1/reset_password/', views.ResetPasswordView.as_view(),
         name="account_reset_password"),
    path('v1/verify_otp/', views.VerifyOtpView.as_view(), name="verify_otp"),
    path('v1/authorization/custom_permission_name/',
         views.CustomPermissionView.as_view(), name="custom_permission_name"),
    path('v1/authorization/group_permissions/',
         views.GroupPermissionView.as_view(), name="group_permissions"),
    path('v1/authorization/group_permissions/<int:group_id>/',
         views.GroupPermissionView.as_view(), name="group_permission_operations"),
    path('v1/authorization/assign_group_user/', views.AssignGroupPermissionView.as_view(),
         name="assign_group"),
    path('v1/view_all_users/', views.UserView.as_view(),
         name="user_view"),
    path('v1/authorization/admin_user_email/',
         views.AdminUserEmailView.as_view(), name="admin_user_email"),
    path('v1/authorization/admin_user_verify_otp/',
         views.AdminUserVerifyOtpView.as_view(), name="admin_user_verify_otp"),
    path('v1/authorization/admin_user_register/',
         views.AdminUserRegistrationView.as_view(), name="admin_user_register"),
    path('v1/authorization/get_user_all_permissions/',
         views.GetUserPermissionsView.as_view(), name="get_user_all_permissions"),


]
