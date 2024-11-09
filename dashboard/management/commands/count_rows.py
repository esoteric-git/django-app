import pandas as pd

# Read both files
soil_moisture_path = '/Users/wrandom/Dropbox/Code/clients/ocean/django-app/ocean_analytics/data_src/dg_soil_moisture.csv'
iron_path = '/Users/wrandom/Dropbox/Code/clients/ocean/django-app/ocean_analytics/data_src/Dissovled Iron.csv'

# Count rows
soil_df = pd.read_csv(soil_moisture_path, encoding='latin1')
iron_df = pd.read_csv(iron_path, encoding='latin1')

print("=== Dataset Sizes ===")
print(f"Soil Moisture rows: {len(soil_df):,}")
print(f"Dissolved Iron rows: {len(iron_df):,}")

# Show date range for context
print("\n=== Date Ranges ===")
print("Soil Moisture:")
print(f"First: {soil_df['timestamp'].min()}")
print(f"Last: {soil_df['timestamp'].max()}")

# Memory usage
print("\n=== Memory Usage ===")
print(f"Soil Moisture: {soil_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
print(f"Dissolved Iron: {iron_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")