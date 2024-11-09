from django.core.management.base import BaseCommand
import pandas as pd
from dashboard.models import SoilMoisture
from django.utils.timezone import make_aware
from datetime import datetime
import gc  # For garbage collection

class Command(BaseCommand):
    help = 'Import soil moisture data from CSV'

    def handle(self, *args, **kwargs):
        csv_file = 'ocean_analytics/data_src/dg_soil_moisture.csv'
        chunk_size = 5000  
        
        self.stdout.write("Starting soil moisture data import...")
        try:
            # Clear existing data
            self.stdout.write("Clearing existing data...")
            SoilMoisture.objects.all().delete()
            
            # Process the CSV in chunks
            total_imported = 0
            skipped_rows = 0
            chunk_iterator = pd.read_csv(
                csv_file, 
                encoding='latin1', 
                chunksize=chunk_size,
                usecols=['timestamp', 'year', 'doy', 'hour', 'minute', 'site', 'm_soil', 'sensorZ'],
                dtype={
                    'year': int,
                    'doy': int,
                    'hour': int,
                    'minute': int,
                    'site': str,
                    'm_soil': float,
                    'sensorZ': float
                },
                na_values=['', 'NA', 'NaN']
            )
            
            for chunk_number, chunk in enumerate(chunk_iterator, 1):
                measurements = []
                
                for _, row in chunk.iterrows():
                    try:
                        # Skip row if essential time components are missing
                        if pd.isna(row['year']) or pd.isna(row['doy']) or pd.isna(row['hour']) or pd.isna(row['minute']):
                            skipped_rows += 1
                            continue
                            
                        # Construct datetime from components
                        date_str = f"{int(row['year'])}-{int(row['doy']):03d} {int(row['hour']):02d}:{int(row['minute']):02d}:00"
                        dt = pd.to_datetime(date_str, format='%Y-%j %H:%M:%S')
                        dt = make_aware(dt)
                        
                        # Get soil moisture value, might be NaN
                        soil_moisture = row['m_soil'] if not pd.isna(row['m_soil']) else None
                        sensorZ = row['sensorZ'] if not pd.isna(row['sensorZ']) else None
                        
                        measurement = SoilMoisture(
                            datetime=dt,
                            site=row['site'],
                            soil_moisture=soil_moisture,
                            sensorZ=sensorZ
                        )
                        measurements.append(measurement)
                        
                    except Exception as e:
                        skipped_rows += 1
                        self.stdout.write(self.style.WARNING(
                            f'Error on row {total_imported + len(measurements) + 1}: {str(e)}'
                        ))
                
                if measurements:
                    # Use batch size for bulk_create to prevent memory issues
                    batch_size = 1000
                    for i in range(0, len(measurements), batch_size):
                        batch = measurements[i:i + batch_size]
                        SoilMoisture.objects.bulk_create(batch)
                    
                    total_imported += len(measurements)
                    self.stdout.write(
                        f'Progress: Chunk {chunk_number} completed. '
                        f'Total records imported: {total_imported:,}'
                    )
                
                # Force garbage collection after each chunk
                measurements = None
                gc.collect()
                
            self.stdout.write(self.style.SUCCESS(
                f'Import completed.\n'
                f'Total records imported: {total_imported:,}\n'
                f'Skipped rows: {skipped_rows:,}'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))