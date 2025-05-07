from django.urls import path, include
from .views import *



urlpatterns = [
    path('v1/membership_type/', MembershipTypeView.as_view(), name="membership_type"),
    path('v1/institute_name/', InstituteNameView.as_view(), name="institute_name"),
    path('v1/gender/', GenderView.as_view(), name="gender"),
    path('v1/member_ship_status_choice/', MembershipStatusChoiceView.as_view(), name="membership_status"),
    path("v1/marital_status_choice/", MaritalStatusChoiceView.as_view(), name="marital_status"),
    path('v1/employment_type_choice/', EmploymentTypeChoiceView.as_view(), name="employment_type"),
    path('v1/email_type_choice/', EmailTypeChoiceView.as_view(), name="email_type"),
    path("v1/contact_type_choice/", ContactTypeChoiceView.as_view(), name="contact_type"),
    path('v1/address_type_choice/', AddressTypeChoiceView.as_view(), name="address_type"),
    path("v1/document_type_choice/", DocumentTypeChoiceView.as_view(), name="document_type"),
    path("v1/spouse_status_type_choice/", SpouseStatusChoiceView.as_view(), name="spouse_status"),
    path('v1/descendant_relation_type_choice/', DescendantRelationChoiceView.as_view(), name="descendant_relation"),
    
  
]
