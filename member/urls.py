from django.urls import path
from . import views
urlpatterns = [
    path('v1/members/', views.MemberView.as_view(),
         name="member_view"),
    path('v1/members/get_latest_id/', views.MemberIdView.as_view(),
         name="member_id_view"),
]
