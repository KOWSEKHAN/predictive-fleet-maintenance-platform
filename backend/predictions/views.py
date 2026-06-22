from django.db.models import Max
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Prediction
from .serializers import PredictionSerializer
from fleet.models import Vehicle
from telemetry.models import Telemetry


# ── Pagination ────────────────────────────────────────────────────────────────
class PredictionPagination(PageNumberPagination):
    page_size            = 50
    page_size_query_param = 'page_size'
    max_page_size        = 200


# ── Helper: build telemetry map in ONE query ─────────────────────────────────
def build_telemetry_map(tyre_ids):
    """
    Returns {tyre_id: latest_Telemetry_instance} for the given tyre IDs.
    Single aggregated query instead of 1 query per tyre.
    """
    # Step 1: get the max telemetry id per tyre (1 query)
    latest_ids = (
        Telemetry.objects
        .filter(tyre_id__in=tyre_ids)
        .values('tyre_id')
        .annotate(latest_id=Max('id'))
        .values_list('latest_id', flat=True)
    )
    # Step 2: fetch those telemetry rows (1 query)
    telemetry_qs = Telemetry.objects.filter(id__in=latest_ids).select_related('tyre')
    return {t.tyre_id: t for t in telemetry_qs}


# ── Views ─────────────────────────────────────────────────────────────────────
class PredictionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            return Response(
                {"detail": "User has no associated company."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get latest prediction per tyre — 1 query
        latest_ids = (
            Prediction.objects
            .filter(vehicle__company=company)
            .values('tyre')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        # Fetch with select_related to avoid vehicle/tyre N+1 — 1 query
        predictions = (
            Prediction.objects
            .filter(id__in=latest_ids)
            .select_related('vehicle', 'tyre')
            .order_by('-created_at')
        )

        # Build telemetry map: 2 queries total instead of 3 × N
        tyre_ids = list(predictions.values_list('tyre_id', flat=True))
        telemetry_map = build_telemetry_map(tyre_ids)

        # Paginate
        paginator   = PredictionPagination()
        page        = paginator.paginate_queryset(predictions, request)
        serializer  = PredictionSerializer(
            page, many=True, context={'telemetry_map': telemetry_map}
        )
        return paginator.get_paginated_response(serializer.data)


class VehiclePredictionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vehicle_id):
        company = request.user.company
        if not company:
            return Response(
                {"detail": "User has no associated company."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id, company=company)
        except Vehicle.DoesNotExist:
            return Response({"detail": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND)

        latest_ids = (
            Prediction.objects
            .filter(vehicle=vehicle)
            .values('tyre')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        predictions = (
            Prediction.objects
            .filter(id__in=latest_ids)
            .select_related('vehicle', 'tyre')
            .order_by('tyre__tyre_position')
        )

        tyre_ids      = list(predictions.values_list('tyre_id', flat=True))
        telemetry_map = build_telemetry_map(tyre_ids)

        serializer = PredictionSerializer(
            predictions, many=True, context={'telemetry_map': telemetry_map}
        )
        return Response(serializer.data)


class AlertsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            return Response(
                {"detail": "User has no associated company."},
                status=status.HTTP_400_BAD_REQUEST
            )

        latest_ids = (
            Prediction.objects
            .filter(vehicle__company=company)
            .values('tyre')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        alerts = (
            Prediction.objects
            .filter(id__in=latest_ids, condition__in=['Average', 'Bad'])
            .select_related('vehicle', 'tyre')
            .order_by('-risk_score')
        )

        tyre_ids      = list(alerts.values_list('tyre_id', flat=True))
        telemetry_map = build_telemetry_map(tyre_ids)

        # Paginate alerts too
        paginator  = PredictionPagination()
        page       = paginator.paginate_queryset(alerts, request)
        serializer = PredictionSerializer(
            page, many=True, context={'telemetry_map': telemetry_map}
        )
        return paginator.get_paginated_response(serializer.data)
