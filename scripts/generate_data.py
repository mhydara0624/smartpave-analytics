#!/usr/bin/env python3
"""
Generate realistic pavement condition and maintenance data for SmartPave Analytics.
Creates 16,000 miles of roadway data across 5 years with realistic patterns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_road_network():
    """Generate road network with 16,000 miles of roadway"""
    
    # Create road segments (approximately 16,000 miles)
    n_segments = 8000  # ~2 miles per segment on average
    n_roads = 200      # 200 different roads
    
    roads = []
    segments = []
    
    # Generate roads
    for road_id in range(1, n_roads + 1):
        road_name = f"R{road_id:03d}"
        n_segments_road = np.random.poisson(40)  # Average 40 segments per road
        
        for seg_id in range(1, n_segments_road + 1):
            segment_id = f"{road_name}_S{seg_id:03d}"
            
            # Generate coordinates (simulate real road network)
            base_lat = 39.8283 + np.random.normal(0, 0.5)  # Around Washington DC
            base_lon = -98.5795 + np.random.normal(0, 0.5)
            
            # Add some variation for segments
            lat = base_lat + np.random.normal(0, 0.01)
            lon = base_lon + np.random.normal(0, 0.01)
            
            # Road characteristics
            lanes = np.random.choice([2, 3, 4, 5, 6], p=[0.1, 0.2, 0.4, 0.25, 0.05])
            road_type = np.random.choice(['Highway', 'Arterial', 'Collector', 'Local'], 
                                      p=[0.2, 0.3, 0.3, 0.2])
            
            # Traffic volume (vehicles per day)
            if road_type == 'Highway':
                traffic_volume = np.random.normal(75000, 15000)
            elif road_type == 'Arterial':
                traffic_volume = np.random.normal(35000, 8000)
            elif road_type == 'Collector':
                traffic_volume = np.random.normal(15000, 4000)
            else:  # Local
                traffic_volume = np.random.normal(5000, 2000)
            
            traffic_volume = max(1000, int(traffic_volume))  # Minimum 1000 vehicles/day
            
            roads.append({
                'road_id': road_name,
                'segment_id': segment_id,
                'road_type': road_type,
                'lanes': lanes,
                'latitude': lat,
                'longitude': lon,
                'traffic_volume': traffic_volume,
                'segment_length_miles': np.random.uniform(0.1, 0.5)  # 0.1 to 0.5 miles
            })
    
    return pd.DataFrame(roads)

def generate_pavement_condition_data(roads_df):
    """Generate pavement condition data over 5 years"""
    
    condition_data = []
    
    # Generate data for each quarter from 2020-2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        print(f"Generating data for {current_date.strftime('%Y-%m')}")
        
        for _, road in roads_df.iterrows():
            # Base condition score (100 = perfect, 0 = failed)
            base_score = 85
            
            # Add seasonal variation
            month = current_date.month
            if month in [12, 1, 2]:  # Winter
                seasonal_factor = -5
            elif month in [6, 7, 8]:  # Summer
                seasonal_factor = 2
            else:
                seasonal_factor = 0
            
            # Traffic impact
            traffic_factor = -road['traffic_volume'] / 100000
            
            # Road type impact
            if road['road_type'] == 'Highway':
                road_factor = 5  # Better maintained
            elif road['road_type'] == 'Local':
                road_factor = -3  # Less maintained
            else:
                road_factor = 0
            
            # Random variation
            random_factor = np.random.normal(0, 3)
            
            # Calculate condition score
            condition_score = max(0, min(100, 
                base_score + seasonal_factor + traffic_factor + road_factor + random_factor))
            
            # Generate related metrics
            roughness_index = max(50, 200 - condition_score + np.random.normal(0, 10))
            cracking_percent = max(0, (100 - condition_score) * 0.3 + np.random.normal(0, 2))
            pothole_count = max(0, int((100 - condition_score) / 20 + np.random.poisson(0.5)))
            
            # Weather impact
            precipitation = np.random.exponential(0.5)  # inches
            freeze_thaw_cycles = np.random.poisson(2) if month in [12, 1, 2] else 0
            
            condition_data.append({
                'road_id': road['road_id'],
                'segment_id': road['segment_id'],
                'date': current_date,
                'lanes': road['lanes'],
                'condition_score': round(condition_score, 1),
                'roughness_index': round(roughness_index, 1),
                'cracking_percent': round(cracking_percent, 1),
                'pothole_count': pothole_count,
                'precipitation': round(precipitation, 2),
                'freeze_thaw_cycles': freeze_thaw_cycles,
                'temperature_avg': 50 + 30 * np.sin(2 * np.pi * month / 12) + np.random.normal(0, 5),
                'traffic_volume': road['traffic_volume'],
                'road_type': road['road_type'],
                'latitude': road['latitude'],
                'longitude': road['longitude']
            })
        
        # Move to next quarter
        if current_date.month in [1, 4, 7, 10]:
            if current_date.month == 10:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 3)
        else:
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    return pd.DataFrame(condition_data)

def generate_maintenance_records(condition_df):
    """Generate maintenance records based on condition data"""
    
    maintenance_records = []
    maintenance_id = 1
    
    # Group by segment and analyze condition trends
    for segment_id in condition_df['segment_id'].unique():
        segment_data = condition_df[condition_df['segment_id'] == segment_id].sort_values('date')
        
        last_repair_date = None
        last_condition = 100
        
        for _, row in segment_data.iterrows():
            # Determine if maintenance is needed
            condition_drop = last_condition - row['condition_score']
            
            # Maintenance triggers
            needs_repair = (
                row['condition_score'] < 60 or  # Poor condition
                row['pothole_count'] > 5 or     # Too many potholes
                condition_drop > 15 or          # Rapid deterioration
                (last_repair_date and (row['date'] - last_repair_date).days > 365)  # Annual maintenance
            )
            
            if needs_repair:
                # Determine repair type and cost
                if row['condition_score'] < 40:
                    repair_type = 'resurfacing'
                    base_cost = 50000
                    effectiveness = 0.9
                elif row['pothole_count'] > 3:
                    repair_type = 'pothole_patch'
                    base_cost = 5000
                    effectiveness = 0.7
                elif row['cracking_percent'] > 20:
                    repair_type = 'crack_sealing'
                    base_cost = 15000
                    effectiveness = 0.8
                else:
                    repair_type = 'preventive_maintenance'
                    base_cost = 8000
                    effectiveness = 0.6
                
                # Adjust cost based on road characteristics
                lane_factor = row['lanes'] * 0.2
                traffic_factor = row['traffic_volume'] / 100000
                weather_delay = np.random.poisson(1) if row['precipitation'] > 1 else 0
                
                total_cost = int(base_cost * (1 + lane_factor + traffic_factor))
                
                # Contractor selection
                contractors = ['ABC_Contractors', 'XYZ_Construction', 'Premier_Paving', 
                             'Metro_Maintenance', 'Highway_Experts']
                contractor = np.random.choice(contractors)
                
                maintenance_records.append({
                    'maintenance_id': f'M{maintenance_id:06d}',
                    'road_id': row['road_id'],
                    'segment_id': row['segment_id'],
                    'date': row['date'],
                    'repair_type': repair_type,
                    'cost': total_cost,
                    'effectiveness_score': effectiveness + np.random.normal(0, 0.1),
                    'contractor': contractor,
                    'weather_delay_days': weather_delay,
                    'lanes_affected': row['lanes'],
                    'condition_before': row['condition_score'],
                    'traffic_volume': row['traffic_volume']
                })
                
                maintenance_id += 1
                last_repair_date = row['date']
                last_condition = min(100, row['condition_score'] + 20)  # Improvement after repair
            else:
                last_condition = row['condition_score']
    
    return pd.DataFrame(maintenance_records)

def generate_traffic_data(roads_df):
    """Generate detailed traffic volume data"""
    
    traffic_data = []
    
    for _, road in roads_df.iterrows():
        # Generate monthly traffic data
        for year in range(2020, 2025):
            for month in range(1, 13):
                # Seasonal traffic patterns
                if month in [6, 7, 8]:  # Summer
                    seasonal_factor = 1.1
                elif month in [12, 1, 2]:  # Winter
                    seasonal_factor = 0.9
                else:
                    seasonal_factor = 1.0
                
                # Add some growth over time
                growth_factor = 1 + (year - 2020) * 0.02
                
                monthly_volume = int(road['traffic_volume'] * seasonal_factor * growth_factor * 
                                   np.random.normal(1, 0.1))
                
                traffic_data.append({
                    'road_id': road['road_id'],
                    'segment_id': road['segment_id'],
                    'year': year,
                    'month': month,
                    'avg_daily_traffic': monthly_volume,
                    'peak_hour_factor': np.random.uniform(0.8, 1.2),
                    'truck_percentage': np.random.uniform(0.05, 0.15)
                })
    
    return pd.DataFrame(traffic_data)

def main():
    """Generate all datasets"""
    
    print("Generating SmartPave Analytics datasets...")
    print("=" * 50)
    
    # Create output directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Generate road network
    print("1. Generating road network...")
    roads_df = generate_road_network()
    roads_df.to_csv('data/raw/road_network.csv', index=False)
    print(f"   Generated {len(roads_df)} road segments")
    
    # Generate pavement condition data
    print("2. Generating pavement condition data...")
    condition_df = generate_pavement_condition_data(roads_df)
    condition_df.to_csv('data/raw/pavement_condition_2020-2024.csv', index=False)
    print(f"   Generated {len(condition_df)} condition records")
    
    # Generate maintenance records
    print("3. Generating maintenance records...")
    maintenance_df = generate_maintenance_records(condition_df)
    maintenance_df.to_csv('data/raw/maintenance_records_2020-2024.csv', index=False)
    print(f"   Generated {len(maintenance_df)} maintenance records")
    
    # Generate traffic data
    print("4. Generating traffic data...")
    traffic_df = generate_traffic_data(roads_df)
    traffic_df.to_csv('data/raw/traffic_volume_data.csv', index=False)
    print(f"   Generated {len(traffic_df)} traffic records")
    
    # Generate summary statistics
    total_miles = roads_df['segment_length_miles'].sum()
    total_cost = maintenance_df['cost'].sum()
    
    print("\n" + "=" * 50)
    print("DATASET SUMMARY")
    print("=" * 50)
    print(f"Total road segments: {len(roads_df):,}")
    print(f"Total miles: {total_miles:,.1f}")
    print(f"Condition records: {len(condition_df):,}")
    print(f"Maintenance records: {len(maintenance_df):,}")
    print(f"Total maintenance cost: ${total_cost:,.0f}")
    print(f"Average condition score: {condition_df['condition_score'].mean():.1f}")
    print(f"Average repair cost: ${maintenance_df['cost'].mean():,.0f}")
    
    print("\nFiles generated:")
    print("- data/raw/road_network.csv")
    print("- data/raw/pavement_condition_2020-2024.csv")
    print("- data/raw/maintenance_records_2020-2024.csv")
    print("- data/raw/traffic_volume_data.csv")
    
    print("\n✅ Data generation complete!")

if __name__ == "__main__":
    main()
