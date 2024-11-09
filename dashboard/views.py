from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import IronMeasurement, SoilMoisture
from django.db.models import Avg, Min, Max, Count
from django.utils import timezone
from datetime import timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import TruncMonth, TruncDay

# Create your views here.

class DashboardView(LoginRequiredMixin, ListView):
    model = IronMeasurement
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'measurements'
    paginate_by = 20  # Show 20 records per page
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get data for chart
        chart_data = IronMeasurement.objects.values('datetime', 'rrs_443')[:100]
        context['chart_data'] = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        return context

class AnalyticsDemoView(LoginRequiredMixin, TemplateView):
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
        return IronMeasurement.objects.values('datetime').annotate(avgTemp=Avg('rrs_443')).order_by('-datetime')[:100]

    def get_salinity_data(self):
        return IronMeasurement.objects.values('datetime').annotate(avgSalinity=Avg('rrs_443')).order_by('-datetime')[:100]

    def get_depth_data(self):
        return IronMeasurement.objects.values('datetime').annotate(avgDepth=Avg('depth')).order_by('-datetime')[:100]

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

class DissolvedIronView(LoginRequiredMixin, ListView):
    model = IronMeasurement
    template_name = 'dashboard/dissolved_iron.html'
    context_object_name = 'measurements'
    paginate_by = 20
    
    def get_queryset(self):
        return IronMeasurement.objects.all().order_by('-datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get average DFe by depth ranges
        depth_ranges = {
            'Surface (0-50m)': (0, 50),
            'Mid (50-200m)': (50, 200),
            'Deep (>200m)': (200, float('inf'))
        }
        
        depth_data = []
        for label, (min_depth, max_depth) in depth_ranges.items():
            count = IronMeasurement.objects.filter(
                depth__gte=min_depth,
                depth__lt=max_depth
            ).count()
            print(f"{label}: {count} measurements")
            
            avg_dfe = IronMeasurement.objects.filter(
                depth__gte=min_depth,
                depth__lt=max_depth
            ).aggregate(avg_dfe=Avg('dfe'))['avg_dfe']
            print(f"{label} avg DFe: {avg_dfe}")
            
            depth_data.append({
                'depth_range': label,
                'avg_dfe': avg_dfe
            })
        
        # Get correlation between DFe and Rrs_443
        context['depth_data'] = json.dumps(depth_data)
        
        # Get temporal trends
        monthly_data = (IronMeasurement.objects
                       .annotate(month=TruncMonth('datetime'))
                       .values('month')
                       .annotate(avg_dfe=Avg('dfe'), avg_rrs=Avg('rrs_443'))
                       .order_by('month'))
        
        context['monthly_data'] = json.dumps(list(monthly_data), cls=DjangoJSONEncoder)
        return context

class SoilMoistureView(LoginRequiredMixin, ListView):
    model = SoilMoisture
    template_name = 'dashboard/soil_moisture.html'
    context_object_name = 'measurements'
    paginate_by = 50
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get daily averages by site
        daily_by_site = (SoilMoisture.objects
                        .annotate(date=TruncDay('datetime'))
                        .values('date', 'site')
                        .annotate(
                            avg_moisture=Avg('soil_moisture'),
                            min_moisture=Min('soil_moisture'),
                            max_moisture=Max('soil_moisture')
                        )
                        .order_by('date', 'site'))

        # Get site summary statistics
        site_stats = (SoilMoisture.objects
                     .values('site')
                     .annotate(
                         avg_moisture=Avg('soil_moisture'),
                         min_moisture=Min('soil_moisture'),
                         max_moisture=Max('soil_moisture'),
                         measurements=Count('id')
                     )
                     .order_by('site'))
        
        # Get depth distribution if sensorZ exists
        depth_stats = (SoilMoisture.objects
                      .values('site', 'sensorZ')
                      .annotate(avg_moisture=Avg('soil_moisture'))
                      .order_by('site', 'sensorZ'))
        
        context.update({
            'daily_by_site': json.dumps(list(daily_by_site), cls=DjangoJSONEncoder),
            'site_stats': json.dumps(list(site_stats), cls=DjangoJSONEncoder),
            'depth_stats': json.dumps(list(depth_stats), cls=DjangoJSONEncoder)
        })
        return context
