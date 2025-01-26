from django.urls import path
from . import views
urlpatterns = [
    path('v1/register_club/', views.ClubRegisterView.as_view(),
         name="club_registration"),

]
