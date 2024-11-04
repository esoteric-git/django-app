from django.core.management.base import BaseCommand
from dashboard.models import OceanMetric
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Populates the database with mock ocean metric data'

    def handle(self, *args, **kwargs):
        OceanMetric.objects.all().delete()  # Clear existing data
        
        locations = ['Pacific Ocean', 'Atlantic Ocean', 'Indian Ocean', 'Southern Ocean', 'Arctic Ocean']
        
        for i in range(1000):  # Generate 1000 data points
            OceanMetric.objects.create(
                timestamp=timezone.now() - timedelta(hours=i),
                location=random.choice(locations),
                temperature=random.uniform(0, 30),
                salinity=random.uniform(30, 38),
                depth=random.randint(0, 5000)
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated mock data'))
