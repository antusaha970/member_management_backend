
from django.urls import path
from .views import ActivityLogAPIView,AllUserActivityLogAPIView

urlpatterns = [
    path("v1/activity/user_activity/", ActivityLogAPIView.as_view(), name="user_activity"),
    path("v1/activity/all_user_activity/", AllUserActivityLogAPIView.as_view(), name="all_user_activity"),
]