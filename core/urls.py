from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register("v1/gender", GenderViewSet)


urlpatterns = [
    path('v1/membership_type/', MembershipTypeView.as_view(), name="membership_type"),
    path('v1/institute_name/', InstituteNameView.as_view(), name="institute_name"),
    path('', include(router.urls))
]
