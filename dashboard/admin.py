from django.contrib import admin
from .models import OceanMetric

# Register your models here.

@admin.register(OceanMetric)
class OceanMetricAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'location', 'temperature', 'salinity', 'depth')
    list_filter = ('location',)
    date_hierarchy = 'timestamp'
