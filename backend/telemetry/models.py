from django.db import models
from fleet.models import Vehicle, Tyre

class Telemetry(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='telemetry')
    tyre = models.ForeignKey(Tyre, on_delete=models.CASCADE, related_name='telemetry')
    psi = models.FloatField()
    depth = models.FloatField()
    temperature = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Telemetry {self.id} for Vehicle {self.vehicle.vehicle_number} - Tyre {self.tyre.tyre_position}"
