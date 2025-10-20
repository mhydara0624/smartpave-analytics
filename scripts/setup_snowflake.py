#!/usr/bin/env python3
"""
Setup script for SmartPave Analytics in Snowflake.
Creates necessary databases, schemas, and stages for the project.
"""

import snowflake.connector
import yaml
import os

def load_config():
    """Load configuration from YAML file"""
    with open('../config/snowflake_config.yaml', 'r') as file:
        return yaml.safe_load(file)

def create_snowflake_objects(conn, config):
    """Create necessary Snowflake objects"""
    cursor = conn.cursor()
    
    try:
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']}")
        print(f"✅ Database {config['database']} created/verified")
        
        # Use database
        cursor.execute(f"USE DATABASE {config['database']}")
        
        # Create schema
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {config['schema']}")
        print(f"✅ Schema {config['schema']} created/verified")
        
        # Use schema
        cursor.execute(f"USE SCHEMA {config['schema']}")
        
        # Create stages for data storage
        cursor.execute(f"CREATE STAGE IF NOT EXISTS {config['raw_data_stage']}")
        cursor.execute(f"CREATE STAGE IF NOT EXISTS {config['processed_data_stage']}")
        cursor.execute(f"CREATE STAGE IF NOT EXISTS {config['models_stage']}")
        print("✅ Data stages created/verified")
        
        # Create tables for structured data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS road_segments (
                segment_id VARCHAR(50) PRIMARY KEY,
                road_id VARCHAR(50),
                road_type VARCHAR(50),
                lanes INTEGER,
                latitude FLOAT,
                longitude FLOAT,
                traffic_volume INTEGER,
                segment_length_miles FLOAT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pavement_condition (
                record_id VARCHAR(50) PRIMARY KEY,
                segment_id VARCHAR(50),
                date DATE,
                condition_score FLOAT,
                roughness_index FLOAT,
                cracking_percent FLOAT,
                pothole_count INTEGER,
                precipitation FLOAT,
                freeze_thaw_cycles INTEGER,
                temperature_avg FLOAT,
                FOREIGN KEY (segment_id) REFERENCES road_segments(segment_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_records (
                maintenance_id VARCHAR(50) PRIMARY KEY,
                segment_id VARCHAR(50),
                date DATE,
                repair_type VARCHAR(50),
                cost FLOAT,
                effectiveness_score FLOAT,
                contractor VARCHAR(100),
                weather_delay_days INTEGER,
                FOREIGN KEY (segment_id) REFERENCES road_segments(segment_id)
            )
        """)
        
        print("✅ Data tables created/verified")
        
        # Create views for analysis
        cursor.execute("""
            CREATE OR REPLACE VIEW pavement_analysis AS
            SELECT 
                pc.segment_id,
                rs.road_type,
                rs.lanes,
                rs.traffic_volume,
                pc.date,
                pc.condition_score,
                pc.roughness_index,
                pc.cracking_percent,
                pc.pothole_count,
                COALESCE(mr.total_cost, 0) as total_maintenance_cost,
                COALESCE(mr.repair_count, 0) as repair_count
            FROM pavement_condition pc
            JOIN road_segments rs ON pc.segment_id = rs.segment_id
            LEFT JOIN (
                SELECT 
                    segment_id,
                    SUM(cost) as total_cost,
                    COUNT(*) as repair_count
                FROM maintenance_records
                GROUP BY segment_id
            ) mr ON pc.segment_id = mr.segment_id
        """)
        
        print("✅ Analysis views created/verified")
        
    except Exception as e:
        print(f"❌ Error creating Snowflake objects: {e}")
        raise
    finally:
        cursor.close()

def main():
    """Main setup function"""
    print("Setting up SmartPave Analytics in Snowflake...")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Note: In a real implementation, you would connect to Snowflake here
    # For this demo, we'll just show what would be created
    print("Configuration loaded:")
    print(f"  Database: {config['database']}")
    print(f"  Schema: {config['schema']}")
    print(f"  Warehouse: {config['warehouse_size']}")
    
    print("\nTo complete setup, run these SQL commands in Snowflake:")
    print("=" * 50)
    
    print(f"CREATE DATABASE IF NOT EXISTS {config['database']};")
    print(f"USE DATABASE {config['database']};")
    print(f"CREATE SCHEMA IF NOT EXISTS {config['schema']};")
    print(f"USE SCHEMA {config['schema']};")
    print(f"CREATE STAGE IF NOT EXISTS {config['raw_data_stage']};")
    print(f"CREATE STAGE IF NOT EXISTS {config['processed_data_stage']};")
    print(f"CREATE STAGE IF NOT EXISTS {config['models_stage']};")
    
    print("\n✅ Setup script completed!")
    print("Next steps:")
    print("1. Run the SQL commands above in Snowflake")
    print("2. Upload data files to the stages")
    print("3. Run the notebooks to begin analysis")

if __name__ == "__main__":
    main()
