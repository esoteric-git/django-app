from django.db import models

# Create your models here.

class OceanMetric(models.Model):
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=100)
    temperature = models.FloatField()
    salinity = models.FloatField()
    depth = models.IntegerField()

    def __str__(self):
        return f"{self.location} - {self.timestamp}"
