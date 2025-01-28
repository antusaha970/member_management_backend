from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register("v1/gender", GenderViewSet)
router.register("v1/member_ship_status_choice", MembershipStatusChoiceViewSet)
router.register("v1/marital_status_choice", MaritalStatusChoiceViewSet)


urlpatterns = [
    path('v1/membership_type/', MembershipTypeView.as_view(), name="membership_type"),
    path('v1/institute_name/', InstituteNameView.as_view(), name="institute_name"),
    path('', include(router.urls))
]
