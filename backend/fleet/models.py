from django.db import models
from accounts.models import Company

class Vehicle(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=255)
    route = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='Healthy') # e.g. Healthy, Warning, Critical
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vehicle_number

class Tyre(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='tyres')
    tyre_position = models.CharField(max_length=20) # e.g. Front Left, Rear Left Outer, etc.
    installation_date = models.DateField()

    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.tyre_position}"
