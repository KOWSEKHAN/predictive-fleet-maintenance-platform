from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Vehicle, Tyre
from .serializers import VehicleSerializer, TyreSerializer


# ── Pagination ────────────────────────────────────────────────────────────────
class VehiclePagination(PageNumberPagination):
    page_size             = 25
    page_size_query_param = 'page_size'
    max_page_size         = 100


# ── Vehicle endpoints ─────────────────────────────────────────────────────────
class VehicleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            return Response(
                {"detail": "User has no associated company."},
                status=status.HTTP_400_BAD_REQUEST
            )
        vehicles = Vehicle.objects.filter(company=company).order_by('vehicle_number')

        paginator  = VehiclePagination()
        page       = paginator.paginate_queryset(vehicles, request)
        serializer = VehicleSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        company = request.user.company
        if not company:
            return Response(
                {"detail": "User has no associated company."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VehicleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        company = request.user.company
        try:
            vehicle = Vehicle.objects.get(pk=pk, company=company)
        except Vehicle.DoesNotExist:
            return Response({"detail": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)


class VehicleTyresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        company = request.user.company
        try:
            vehicle = Vehicle.objects.get(pk=pk, company=company)
        except Vehicle.DoesNotExist:
            return Response({"detail": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND)
        tyres      = Tyre.objects.filter(vehicle=vehicle)
        serializer = TyreSerializer(tyres, many=True)
        return Response(serializer.data)


# ── Dashboard Summary: 1 DB query instead of 4 ───────────────────────────────
class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            return Response(
                {"detail": "User has no associated company."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Single aggregation query instead of 4 separate .count() calls
        counts = (
            Vehicle.objects
            .filter(company=company)
            .values('status')
            .annotate(n=Count('id'))
        )

        status_map = {row['status']: row['n'] for row in counts}
        total_vehicles    = sum(status_map.values())
        healthy_vehicles  = status_map.get('Healthy',  0)
        warning_vehicles  = status_map.get('Warning',  0)
        critical_vehicles = status_map.get('Critical', 0)

        if total_vehicles > 0:
            fleet_health_score = int(
                (healthy_vehicles * 100 + warning_vehicles * 60 + critical_vehicles * 20)
                / total_vehicles
            )
        else:
            fleet_health_score = 100

        return Response({
            'total_vehicles':    total_vehicles,
            'healthy_vehicles':  healthy_vehicles,
            'warning_vehicles':  warning_vehicles,
            'critical_vehicles': critical_vehicles,
            'fleet_health_score': fleet_health_score,
        })


# ── Aggregated chart data: replaces full predictions fetch on Dashboard ───────
class DashboardChartDataView(APIView):
    """
    Returns pre-aggregated data for the two dashboard charts:
    1. Condition distribution (Pie chart) — counts per condition
    2. Worst 8 vehicles by min remaining_km (Bar chart)

    Eliminates the need for the frontend to fetch all 300 predictions
    just to derive chart data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Min, Max
        from predictions.models import Prediction

        company = request.user.company
        if not company:
            return Response(
                {"detail": "User has no associated company."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Latest prediction id per tyre (1 query)
        latest_ids = (
            Prediction.objects
            .filter(vehicle__company=company)
            .values('tyre')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        # Condition distribution — 1 query
        condition_counts = (
            Prediction.objects
            .filter(id__in=latest_ids)
            .values('condition')
            .annotate(count=Count('id'))
        )
        pie_data = [{'condition': row['condition'], 'count': row['count']}
                    for row in condition_counts]

        # Worst 8 vehicles by lowest remaining_km — 1 query
        worst_vehicles = (
            Prediction.objects
            .filter(id__in=latest_ids)
            .values('vehicle__vehicle_number')
            .annotate(min_remaining_km=Min('remaining_km'))
            .order_by('min_remaining_km')[:8]
        )
        bar_data = [
            {'name': row['vehicle__vehicle_number'], 'km': row['min_remaining_km']}
            for row in worst_vehicles
        ]

        return Response({'pie_data': pie_data, 'bar_data': bar_data})
