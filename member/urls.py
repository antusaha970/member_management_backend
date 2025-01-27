from django.urls import path
from . import views
urlpatterns = [
    path('v1/members/', views.MemberView.as_view(),
         name="member_view"),
]
