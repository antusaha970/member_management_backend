
from django.urls import path
from .views import ActivityLogAPIView

urlpatterns = [
    path("v1/user_activity/", ActivityLogAPIView.as_view(), name="user_activity"),
]