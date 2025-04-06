
from django.urls import path
from event.views import EventVenueView,EventView
urlpatterns = [
    path("v1/events/venue/",EventVenueView.as_view(),name="events_venue"),
    path("v1/events/",EventView.as_view(),name="events"),
]


