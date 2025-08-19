from django.urls import path
from .import views
urlpatterns = [
    path("v1/dashboard_cards/", views.DashboardCardView.as_view(),
         name="dashboard_card_view"),
    path("v1/dashboard_cards/kpi/", views.DashBoardKPICard.as_view(),
         name="dashboard_card_kpi_view"),
    path("v1/membership_chart/", views.DashboardChartView.as_view(),
         name="dashboard_chart_view"),
    path("v1/membership_chart/pie_chart/", views.DashboardPieChartView.as_view(),
         name="dashboard_chart_pie_view"),
]
