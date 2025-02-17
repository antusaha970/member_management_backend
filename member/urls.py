from django.urls import path
from . import views
urlpatterns = [
    path('v1/members/', views.MemberView.as_view(),
         name="member_view"),
    path('v1/members/contact_numbers/', views.MemberContactNumberView.as_view(),
         name="member_contact_number_view"),
    path('v1/members/email_address/', views.MemberEmailAddressView.as_view(),
         name="member_email_address_view"),
    path('v1/members/address/', views.MemberAddressView.as_view(),
         name="member_address_view"),
    path('v1/members/spouse/', views.MemberSpouseView.as_view(),
         name="member_spouse_view"),
    path('v1/members/descendants/', views.MemberDescendsView.as_view(),
         name="member_descendants_view"),
    path('v1/members/job/', views.MemberJobView.as_view(),
         name="member_job_view"),
    path('v1/members/emergency_contact/', views.MemberEmergencyContactView.as_view(),
         name="member_emergency_contact_view"),
    path('v1/members/companion/', views.MemberCompanionView.as_view(),
         name="member_companion_view"),
    path('v1/members/documents/', views.MemberDocumentView.as_view(),
         name="member_documents_view"),
    path('v1/members/get_latest_id/', views.MemberIdView.as_view(),
         name="member_id_view"),
    path('v1/members/<str:member_id>/', views.MemberView.as_view(),
         name="member_update_view"),

]
