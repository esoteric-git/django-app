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
from .forms import SignUpForm, IronMeasurementFilterForm, SoilMoistureFilterForm
from django.db.models import Q

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
    paginate_by = 20
    ordering = ['-datetime']

    def get_queryset(self):
        queryset = super().get_queryset()
        form = IronMeasurementFilterForm(self.request.GET)
        
        if form.is_valid():
            if cruise := form.cleaned_data.get('cruise'):
                queryset = queryset.filter(cruise__icontains=cruise)
            
            if date_from := form.cleaned_data.get('date_from'):
                queryset = queryset.filter(datetime__date__gte=date_from)
                
            if date_to := form.cleaned_data.get('date_to'):
                queryset = queryset.filter(datetime__date__lte=date_to)
                
            if depth_min := form.cleaned_data.get('depth_min'):
                queryset = queryset.filter(depth__gte=depth_min)
                
            if depth_max := form.cleaned_data.get('depth_max'):
                queryset = queryset.filter(depth__lte=depth_max)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = IronMeasurementFilterForm(self.request.GET)
        
        # Add existing chart data
        depth_data = (self.get_queryset()  # Use filtered queryset
            .values('depth')
            .annotate(avg_dfe=Avg('dfe'))
            .order_by('depth'))
        
        for item in depth_data:
            if item['depth']:
                item['depth_range'] = f"{int(item['depth'])}m"
            else:
                item['depth_range'] = 'Unknown'
                
        monthly_data = (self.get_queryset()  # Use filtered queryset
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
    paginate_by = 20
    ordering = ['-datetime']

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SoilMoistureFilterForm(self.request.GET)
        
        if form.is_valid():
            if site := form.cleaned_data.get('site'):
                queryset = queryset.filter(site__icontains=site)
            
            if date_from := form.cleaned_data.get('date_from'):
                queryset = queryset.filter(datetime__date__gte=date_from)
                
            if date_to := form.cleaned_data.get('date_to'):
                queryset = queryset.filter(datetime__date__lte=date_to)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = SoilMoistureFilterForm(self.request.GET)
        
        # Site averages for the bar chart
        site_stats = (self.get_queryset()
            .values('site')
            .annotate(avg_moisture=Avg('soil_moisture'))
            .order_by('site'))
            
        # Daily averages by site for the time series
        daily_by_site = (self.get_queryset()
            .annotate(date=TruncDay('datetime'))
            .values('site', 'date')
            .annotate(avg_moisture=Avg('soil_moisture'))
            .order_by('site', 'date'))

        # Format the data for the charts
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
