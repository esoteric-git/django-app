import pandas as pd
import numpy as np

# Read both files
soil_moisture_path = '/Users/wrandom/Dropbox/Code/clients/ocean/django-app/ocean_analytics/data_src/dg_soil_moisture.csv'
iron_path = '/Users/wrandom/Dropbox/Code/clients/ocean/django-app/ocean_analytics/data_src/Dissovled Iron.csv'

# Read soil moisture data
soil_df = pd.read_csv(soil_moisture_path, encoding='latin1')

# Read iron data, handling the different date format
iron_df = pd.read_csv(iron_path, encoding='latin1')
iron_df['datetime'] = pd.to_datetime(iron_df['datetime'], format='mixed')

print("=== Soil Moisture Data ===")
print("\nTime range:")
print("Start:", soil_df['timestamp'].min())
print("End:", soil_df['timestamp'].max())
print("\nUnique sites:", sorted(soil_df['site'].unique()))

print("\n=== Iron Data ===")
print("\nTime range:")
print("Start:", iron_df['datetime'].min())
print("End:", iron_df['datetime'].max())
print("\nLocation ranges:")
print("Latitude range:", iron_df['lat'].min(), "to", iron_df['lat'].max())
print("Longitude range:", iron_df['lon'].min(), "to", iron_df['lon'].max())

# Check for temporal overlap
soil_df['datetime'] = pd.to_datetime(soil_df['timestamp'])
overlapping_dates = set(soil_df['datetime'].dt.date) & set(iron_df['datetime'].dt.date)

print("\n=== Temporal Overlap ===")
if overlapping_dates:
    print(f"Found {len(overlapping_dates)} overlapping dates")
    print("Sample overlapping dates:", sorted(list(overlapping_dates))[:5])
    
    # For overlapping dates, let's look at the data
    for date in sorted(list(overlapping_dates))[:2]:
        print(f"\nData for {date}:")
        print("\nSoil Moisture sites:")
        soil_data = soil_df[soil_df['datetime'].dt.date == date]['site'].unique()
        print(soil_data)
        
        print("\nIron measurements:")
        iron_data = iron_df[iron_df['datetime'].dt.date == date][['lat', 'lon', 'depth']]
        print(iron_data)