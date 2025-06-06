from django.urls import path
from . import views
urlpatterns = [
    path('v1/members/', views.MemberView.as_view(),
         name="member_view"),
    path('v1/members/list/', views.MemberListView.as_view(),
         name="member_list_view"),
    path('v1/members/contact_numbers/', views.MemberContactNumberView.as_view(),
         name="member_contact_number_view"),
    path('v1/members/contact_numbers/<str:member_ID>/', views.MemberContactNumberView.as_view(),
         name="member_contact_number_view"),
    path('v1/members/email_address/', views.MemberEmailAddressView.as_view(),
         name="member_email_address_view"),
    path('v1/members/email_address/<str:member_ID>/', views.MemberEmailAddressView.as_view(),
         name="member_email_address_view"),
    path('v1/members/address/', views.MemberAddressView.as_view(),
         name="member_address_view"),
    path('v1/members/address/<str:member_ID>/', views.MemberAddressView.as_view(),
         name="member_address_view"),
    path('v1/members/spouse/', views.MemberSpouseView.as_view(),
         name="member_spouse_view"),
    path('v1/members/descendants/', views.MemberDescendsView.as_view(),
         name="member_descendants_view"),
    path('v1/members/job/', views.MemberJobView.as_view(),
         name="member_job_view"),
    path('v1/members/job/<str:member_ID>/', views.MemberJobView.as_view(),
         name="member_job_view"),
    path('v1/members/emergency_contact/', views.MemberEmergencyContactView.as_view(),
         name="member_emergency_contact_view"),
    path('v1/members/emergency_contact/<str:member_ID>/', views.MemberEmergencyContactView.as_view(),
         name="member_emergency_contact_view"),
    path('v1/members/companion/', views.MemberCompanionView.as_view(),
         name="member_companion_view"),
    path('v1/members/documents/', views.MemberDocumentView.as_view(),
         name="member_documents_view"),
    path('v1/members/get_latest_id/', views.MemberIdView.as_view(),
         name="member_id_view"),
    path('v1/members/membership_type/', views.AddMemberIDview.as_view(),
         name="member_add_id_view"),
    path('v1/members/history/', views.MemberHistoryView.as_view(),
         name="member_history_view"),
    path('v1/members/special_day/', views.MemberSpecialDayView.as_view(),
         name="member_special_day_view"),
    path('v1/members/special_day/<str:member_ID>/',
         views.MemberSpecialDayView.as_view(), name="member_special_day_update_view"),
    path('v1/members/certificate/', views.MemberCertificateView.as_view(),
         name="certificate"),
    path('v1/members/history/<str:member_ID>/', views.MemberSingleHistoryView.as_view(),
         name="member_history_single_view"),
    path('v1/members/<str:member_id>/', views.MemberView.as_view(),
         name="member_update_and_delete_view"),


]
