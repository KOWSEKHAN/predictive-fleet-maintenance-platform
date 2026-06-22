from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .simulator import start_background_simulator, stop_background_simulator, simulator_running

class StartSimulatorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = request.user.company
        with open('debug.txt', 'a') as f:
            f.write(f"StartSimulatorView post: user={request.user}, company={company}\n")
        if company:
            from .simulator import generate_demo_fleet_for_company
            generate_demo_fleet_for_company(company)
            
        started = start_background_simulator(interval=5)
        if started:
            return Response({'status': 'running', 'message': 'Simulator started successfully.'})
        return Response({'status': 'running', 'message': 'Simulator is already running.'})

class StopSimulatorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stopped = stop_background_simulator()
        if stopped:
            return Response({'status': 'stopped', 'message': 'Simulator stopped successfully.'})
        return Response({'status': 'stopped', 'message': 'Simulator was not running.'})

class SimulatorStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        global simulator_running
        return Response({'status': 'running' if simulator_running else 'stopped'})
