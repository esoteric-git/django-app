from django.contrib import admin
from .models import IronMeasurement, SoilMoisture

# Register your models here.

@admin.register(IronMeasurement)
class IronMeasurementAdmin(admin.ModelAdmin):
    list_display = ('cruise', 'datetime', 'lat', 'lon', 'depth', 'dfe', 'rrs_443')
    list_filter = ('cruise',)
    date_hierarchy = 'datetime'

@admin.register(SoilMoisture)
class SoilMoistureAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'site', 'soil_moisture', 'sensorZ')
    list_filter = ('site',)
    date_hierarchy = 'datetime'
