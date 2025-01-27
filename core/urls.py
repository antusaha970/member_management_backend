from django.urls import path,include
from .views import *
urlpatterns = [
    path('v1/membership_type/',MembershipTypeView.as_view(),name="membership_type"),
    path('v1/institute_name/',InstituteNameView.as_view(),name="institute_name"),
]
