from django.urls import path
from .views import VehicleListView, VehicleDetailView, VehicleTyresView, DashboardSummaryView, DashboardChartDataView

urlpatterns = [
    path('dashboard/summary',    DashboardSummaryView.as_view(),   name='dashboard-summary'),
    path('dashboard/chart-data', DashboardChartDataView.as_view(), name='dashboard-chart-data'),
    path('vehicles',             VehicleListView.as_view(),         name='vehicle-list'),
    path('vehicles/<int:pk>',    VehicleDetailView.as_view(),       name='vehicle-detail'),
    path('vehicles/<int:pk>/tyres', VehicleTyresView.as_view(),    name='vehicle-tyres'),
]
