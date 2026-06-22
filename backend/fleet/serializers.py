from rest_framework import serializers
from .models import Vehicle, Tyre

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'company', 'vehicle_number', 'vehicle_type', 'driver_name', 'route', 'status', 'created_at']
        read_only_fields = ['company']

class TyreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tyre
        fields = ['id', 'vehicle', 'tyre_position', 'installation_date']
