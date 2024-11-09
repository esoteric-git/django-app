from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import IronMeasurement, SoilMoisture
from django.db.models import Avg, Min, Max, Count
from django.utils import timezone
from datetime import timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import TruncMonth, TruncDay
from django.contrib.auth import login
from .forms import SignUpForm

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

class HomeView(TemplateView):
    template_name = 'dashboard/home.html'

class DissolvedIronView(ListView):
    model = IronMeasurement
    template_name = 'dashboard/dissolved_iron.html'
    context_object_name = 'measurements'
    paginate_by = 20  # Add this line for pagination
    ordering = ['-datetime']  # Add this for consistent ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get depth ranges for chart
        depth_data = (IronMeasurement.objects
            .values('depth')
            .annotate(avg_dfe=Avg('dfe'))
            .order_by('depth'))
        
        # Format depth ranges for display
        for item in depth_data:
            if item['depth']:
                item['depth_range'] = f"{int(item['depth'])}m"
            else:
                item['depth_range'] = 'Unknown'
                
        # Get monthly averages
        monthly_data = (IronMeasurement.objects
            .annotate(month=TruncMonth('datetime'))
            .values('month')
            .annotate(
                avg_dfe=Avg('dfe'),
                avg_rrs=Avg('rrs_443')
            )
            .order_by('month'))

        context['depth_data'] = json.dumps(list(depth_data))
        context['monthly_data'] = json.dumps(list(monthly_data), default=str)
        return context

class SoilMoistureView(ListView):
    model = SoilMoisture
    template_name = 'dashboard/soil_moisture.html'
    context_object_name = 'measurements'
    paginate_by = 20  # Add this line for pagination
    ordering = ['-datetime']  # Add this for consistent ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate site statistics
        site_stats = (SoilMoisture.objects
            .values('site')
            .annotate(avg_moisture=Avg('soil_moisture'))
            .order_by('site'))
            
        # Get daily averages by site
        daily_by_site = (SoilMoisture.objects
            .values('site', 'datetime')
            .annotate(avg_moisture=Avg('soil_moisture'))
            .order_by('site', 'datetime'))

        context['site_stats'] = json.dumps(list(site_stats))
        context['daily_by_site'] = json.dumps(
            list(daily_by_site), 
            default=str
        )
        return context

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
