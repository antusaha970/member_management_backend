from django.urls import path
from . import views
urlpatterns = [
    path('v1/clubs/', views.ClubView.as_view(),
         name="club_registration"),

]
