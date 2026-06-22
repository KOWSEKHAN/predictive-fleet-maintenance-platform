from rest_framework import serializers
from .models import Prediction
from telemetry.models import Telemetry


class PredictionSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    driver_name    = serializers.CharField(source='vehicle.driver_name',    read_only=True)
    tyre_position  = serializers.CharField(source='tyre.tyre_position',     read_only=True)

    # Legacy frontend compatibility fields
    tyre_id = serializers.CharField(source='tyre.tyre_position', read_only=True)
    psi     = serializers.SerializerMethodField()
    depth   = serializers.SerializerMethodField()
    temp    = serializers.SerializerMethodField()
    replace = serializers.SerializerMethodField()

    class Meta:
        model  = Prediction
        fields = [
            'id', 'vehicle', 'vehicle_number', 'driver_name', 'tyre',
            'tyre_position', 'tyre_id', 'condition', 'remaining_km',
            'risk_score', 'created_at', 'psi', 'depth', 'temp', 'replace',
        ]

    # ------------------------------------------------------------------
    # Telemetry is fetched ONCE per serializer instance via context, then
    # cached in a dict keyed by tyre_id — eliminates the N+1 query pattern
    # (previously: 3 separate SELECT queries per prediction row = ~900 extra
    # queries for 300 rows).  The view now passes a `telemetry_map` in context.
    # ------------------------------------------------------------------
    def _get_telemetry(self, obj):
        telemetry_map = self.context.get('telemetry_map')
        if telemetry_map is not None:
            return telemetry_map.get(obj.tyre_id)
        # Fallback for single-object serialisation (e.g. detail views)
        return Telemetry.objects.filter(tyre=obj.tyre).order_by('-timestamp').first()

    def get_psi(self, obj):
        t = self._get_telemetry(obj)
        return t.psi if t else 95.0

    def get_depth(self, obj):
        t = self._get_telemetry(obj)
        return t.depth if t else 8.0

    def get_temp(self, obj):
        t = self._get_telemetry(obj)
        return t.temperature if t else 30.0

    def get_replace(self, obj):
        return obj.condition == 'Bad' or obj.remaining_km <= 0
