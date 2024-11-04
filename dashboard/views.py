from django.shortcuts import render
from django.views.generic import TemplateView
from .models import OceanMetric
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.

class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temperature_data = self.get_temperature_data()
        context['temperature_data'] = temperature_data
        context['temperature_data_json'] = json.dumps(list(temperature_data), cls=DjangoJSONEncoder)
        context['salinity_data'] = self.get_salinity_data()
        context['depth_data'] = self.get_depth_data()
        return context

    def get_temperature_data(self):
        return OceanMetric.objects.values('timestamp').annotate(avgTemp=Avg('temperature')).order_by('-timestamp')[:30]

    def get_salinity_data(self):
        return OceanMetric.objects.values('timestamp').annotate(avg_salinity=Avg('salinity')).order_by('-timestamp')[:30]

    def get_depth_data(self):
        return OceanMetric.objects.values('timestamp').annotate(avg_depth=Avg('depth')).order_by('-timestamp')[:30]

class AnalyticsDemoView(TemplateView):
    template_name = 'dashboard/analytics_demo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temperature_data = self.get_temperature_data()
        salinity_data = self.get_salinity_data()
        depth_data = self.get_depth_data()

        context['temperature_data'] = temperature_data
        context['salinity_data'] = salinity_data
        context['depth_data'] = depth_data

        context['temperature_data_json'] = json.dumps(list(temperature_data), cls=DjangoJSONEncoder)
        context['salinity_data_json'] = json.dumps(list(salinity_data), cls=DjangoJSONEncoder)
        context['depth_data_json'] = json.dumps(list(depth_data), cls=DjangoJSONEncoder)

        return context

    def get_temperature_data(self):
        return OceanMetric.objects.values('timestamp').annotate(avgTemp=Avg('temperature')).order_by('-timestamp')[:100]

    def get_salinity_data(self):
        return OceanMetric.objects.values('timestamp').annotate(avgSalinity=Avg('salinity')).order_by('-timestamp')[:100]

    def get_depth_data(self):
        return OceanMetric.objects.values('timestamp').annotate(avgDepth=Avg('depth')).order_by('-timestamp')[:100]
