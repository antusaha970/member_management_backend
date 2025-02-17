from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register("v1/gender", GenderViewSet)
router.register("v1/member_ship_status_choice", MembershipStatusChoiceViewSet)
router.register("v1/marital_status_choice", MaritalStatusChoiceViewSet)
router.register("v1/employment_type_choice", EmploymentTypeChoiceViewSet)
router.register("v1/email_type_choice", EmailTypeChoiceViewSet)
router.register("v1/contact_type_choice", ContactTypeChoiceViewSet)
router.register("v1/address_type_choice", AddressTypeChoiceViewSet)
router.register("v1/document_type_choice", DocumentTypeChoiceViewSet)
router.register("v1/spouse_status_type_choice", SpouseStatusChoiceViewSet)
router.register("v1/descendant_relation_type_choice",
                DescendantRelationChoiceViewSet)


urlpatterns = [
    path('v1/membership_type/', MembershipTypeView.as_view(), name="membership_type"),
    path('v1/institute_name/', InstituteNameView.as_view(), name="institute_name"),
    path('', include(router.urls))
]
