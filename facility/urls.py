
from django.urls import path
from .views import FacilityView
urlpatterns = [
    path('v1/facility/', FacilityView.as_view(), name='facilities' ),
    # path('v1/facilities/<int:pk>/', FacilityView.as_view(), name='facility-detail'),
]
