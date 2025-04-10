
from django.urls import path
from .views import FacilityView,FacilityUseFeeView,FacilityDetailView,FacilityBuyView
urlpatterns = [
    path('v1/facilities/', FacilityView.as_view(), name='facilities' ),
    path('v1/facilities/<int:facility_id>/', FacilityDetailView.as_view(), name='facility_detail'),
    path('v1/facility_fees/', FacilityUseFeeView.as_view(), name='facility_fees' ),
    path('v1/facility/buy/', FacilityBuyView.as_view(), name='facility_buy' ),
]
