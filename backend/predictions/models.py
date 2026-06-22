from django.db import models
from fleet.models import Vehicle, Tyre

class Prediction(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='predictions')
    tyre = models.ForeignKey(Tyre, on_delete=models.CASCADE, related_name='predictions')
    condition = models.CharField(max_length=50) # e.g. Good, Average, Bad
    remaining_km = models.IntegerField()
    risk_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.id} for Vehicle {self.vehicle.vehicle_number} - Tyre {self.tyre.tyre_position}"
