from django.core.management.base import BaseCommand
import pandas as pd
from dashboard.models import IronMeasurement
from datetime import datetime

class Command(BaseCommand):
    help = 'Import iron measurement data from CSV'

    def handle(self, *args, **kwargs):
        csv_file = 'ocean_analytics/data_src/Dissovled Iron.csv'
        df = pd.read_csv(csv_file)
        
        # Clear existing data
        IronMeasurement.objects.all().delete()
        
        # Import new data
        measurements = []
        for _, row in df.iterrows():
            try:
                measurement = IronMeasurement(
                    cruise=row['cruise'] if pd.notna(row['cruise']) else None,
                    datetime=pd.to_datetime(row['datetime']),
                    lat=row['lat'],
                    lon=row['lon'],
                    depth=row['depth'] if pd.notna(row['depth']) else None,
                    dfe=row['dfe'] if pd.notna(row['dfe']) else None,
                    rrs_443=row['Rrs_443']
                )
                measurements.append(measurement)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error importing row: {e}'))
                
        IronMeasurement.objects.bulk_create(measurements)
        self.stdout.write(self.style.SUCCESS('Successfully imported iron measurement data')) 