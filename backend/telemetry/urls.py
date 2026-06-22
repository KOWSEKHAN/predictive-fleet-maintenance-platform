from django.urls import path
from .views import StartSimulatorView, StopSimulatorView, SimulatorStatusView

urlpatterns = [
    path('simulator/start', StartSimulatorView.as_view(), name='simulator-start'),
    path('simulator/stop', StopSimulatorView.as_view(), name='simulator-stop'),
    path('simulator/status', SimulatorStatusView.as_view(), name='simulator-status'),
]
