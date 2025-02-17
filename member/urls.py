from django.urls import path
from . import views
urlpatterns = [
    path('v1/members/', views.MemberView.as_view(),
         name="member_view"),
    path('v1/members/contact_numbers/', views.MemberContactNumberView.as_view(),
         name="member_contact_number_view"),
    path('v1/members/email_address/', views.MemberEmailAddressView.as_view(),
         name="member_email_address_view"),
    path('v1/members/get_latest_id/', views.MemberIdView.as_view(),
         name="member_id_view"),
    path('v1/members/<str:member_id>/', views.MemberView.as_view(),
         name="member_update_view"),

]
