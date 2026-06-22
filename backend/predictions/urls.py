from django.urls import path
from .views import PredictionListView, VehiclePredictionsView, AlertsListView

urlpatterns = [
    path('predictions', PredictionListView.as_view(), name='prediction-list'),
    path('predictions/<int:vehicle_id>', VehiclePredictionsView.as_view(), name='vehicle-predictions'),
    path('alerts', AlertsListView.as_view(), name='alerts-list'),
]
