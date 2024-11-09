from django.db import models

# Create your models here.

class IronMeasurement(models.Model):
    cruise = models.CharField(max_length=100, null=True, blank=True)
    datetime = models.DateTimeField()
    lat = models.FloatField()
    lon = models.FloatField()
    depth = models.FloatField(null=True, blank=True)
    dfe = models.FloatField(null=True, blank=True)
    rrs_443 = models.FloatField()
    
    class Meta:
        ordering = ['-datetime']
    
    def __str__(self):
        return f"{self.cruise} - {self.datetime}"

class SoilMoisture(models.Model):
    datetime = models.DateTimeField()
    site = models.CharField(max_length=50)
    soil_moisture = models.FloatField(null=True, blank=True)
    sensorZ = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-datetime']
    
    def __str__(self):
        return f"{self.site} - {self.datetime}"
