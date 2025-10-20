-- SmartPave Analytics: Database Setup
-- Run this script to set up the complete database structure

-- Create database and schema
CREATE DATABASE IF NOT EXISTS DOT_workshop_test;
USE DATABASE DOT_workshop_test;
CREATE SCHEMA IF NOT EXISTS smartpave_analytics;
USE SCHEMA smartpave_analytics;

-- Create stages for data storage
CREATE STAGE IF NOT EXISTS smartpave_stage;
CREATE STAGE IF NOT EXISTS smartpave_processed;
CREATE STAGE IF NOT EXISTS smartpave_models;

-- Create file format for CSV loading
CREATE OR REPLACE FILE FORMAT csv_format
    TYPE = CSV
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null')
    EMPTY_FIELD_AS_NULL = TRUE
    FIELD_OPTIONALLY_ENCLOSED_BY = '"';

-- Create road network table
CREATE TABLE IF NOT EXISTS road_network (
    segment_id VARCHAR(50) PRIMARY KEY,
    road_id VARCHAR(50),
    road_type VARCHAR(50),
    lanes INTEGER,
    latitude FLOAT,
    longitude FLOAT,
    traffic_volume INTEGER,
    segment_length_miles FLOAT
);

-- Create pavement condition table
CREATE TABLE IF NOT EXISTS pavement_condition (
    record_id VARCHAR(50) PRIMARY KEY,
    segment_id VARCHAR(50),
    date DATE,
    lanes INTEGER,
    condition_score FLOAT,
    roughness_index FLOAT,
    cracking_percent FLOAT,
    pothole_count INTEGER,
    precipitation FLOAT,
    freeze_thaw_cycles INTEGER,
    temperature_avg FLOAT,
    traffic_volume INTEGER,
    road_type VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    FOREIGN KEY (segment_id) REFERENCES road_network(segment_id)
);

-- Create maintenance records table
CREATE TABLE IF NOT EXISTS maintenance_records (
    maintenance_id VARCHAR(50) PRIMARY KEY,
    road_id VARCHAR(50),
    segment_id VARCHAR(50),
    date DATE,
    repair_type VARCHAR(50),
    cost FLOAT,
    effectiveness_score FLOAT,
    contractor VARCHAR(100),
    weather_delay_days INTEGER,
    lanes_affected INTEGER,
    condition_before FLOAT,
    traffic_volume INTEGER,
    FOREIGN KEY (segment_id) REFERENCES road_network(segment_id)
);

-- Create traffic data table
CREATE TABLE IF NOT EXISTS traffic_data (
    record_id VARCHAR(50) PRIMARY KEY,
    road_id VARCHAR(50),
    segment_id VARCHAR(50),
    year INTEGER,
    month INTEGER,
    avg_daily_traffic INTEGER,
    peak_hour_factor FLOAT,
    truck_percentage FLOAT,
    FOREIGN KEY (segment_id) REFERENCES road_network(segment_id)
);

-- Create features table (for ML pipeline)
CREATE TABLE IF NOT EXISTS pavement_features (
    record_id VARCHAR(50) PRIMARY KEY,
    segment_id VARCHAR(50),
    date DATE,
    condition_score FLOAT,
    -- Time-based features
    days_since_last_repair INTEGER,
    season INTEGER,
    month INTEGER,
    year INTEGER,
    -- Traffic features
    traffic_stress FLOAT,
    condition_trend FLOAT,
    -- Weather features
    weather_damage FLOAT,
    precipitation_30d_avg FLOAT,
    freeze_thaw_30d_sum INTEGER,
    -- Maintenance features
    total_maintenance_cost FLOAT,
    repair_count INTEGER,
    avg_repair_cost FLOAT,
    avg_effectiveness FLOAT,
    days_since_last_maintenance INTEGER,
    -- Road features
    road_type VARCHAR(50),
    lanes INTEGER,
    traffic_volume INTEGER,
    segment_length_miles FLOAT,
    -- Geospatial features
    latitude FLOAT,
    longitude FLOAT
);

-- Create model results table
CREATE TABLE IF NOT EXISTS model_results (
    record_id VARCHAR(50) PRIMARY KEY,
    segment_id VARCHAR(50),
    date DATE,
    predicted_condition FLOAT,
    predicted_cost FLOAT,
    priority_score FLOAT,
    risk_level VARCHAR(20),
    recommended_action VARCHAR(50),
    confidence_score FLOAT
);

-- Create optimization results table
CREATE TABLE IF NOT EXISTS optimization_results (
    segment_id VARCHAR(50) PRIMARY KEY,
    recommended_budget FLOAT,
    expected_improvement FLOAT,
    roi FLOAT,
    priority_rank INTEGER,
    repair_type VARCHAR(50),
    urgency_level VARCHAR(20),
    cost_benefit_ratio FLOAT
);

-- Create views for analysis
CREATE OR REPLACE VIEW pavement_analysis AS
SELECT 
    pc.segment_id,
    rn.road_id,
    rn.road_type,
    rn.lanes,
    rn.traffic_volume,
    pc.date,
    pc.condition_score,
    pc.roughness_index,
    pc.cracking_percent,
    pc.pothole_count,
    COALESCE(mr.total_cost, 0) as total_maintenance_cost,
    COALESCE(mr.repair_count, 0) as repair_count,
    COALESCE(mr.avg_effectiveness, 0) as avg_effectiveness
FROM pavement_condition pc
JOIN road_network rn ON pc.segment_id = rn.segment_id
LEFT JOIN (
    SELECT 
        segment_id,
        SUM(cost) as total_cost,
        COUNT(*) as repair_count,
        AVG(effectiveness_score) as avg_effectiveness
    FROM maintenance_records
    GROUP BY segment_id
) mr ON pc.segment_id = mr.segment_id;

-- Create view for current conditions
CREATE OR REPLACE VIEW current_conditions AS
SELECT 
    segment_id,
    condition_score,
    pothole_count,
    cracking_percent,
    traffic_volume,
    road_type,
    ROW_NUMBER() OVER (PARTITION BY segment_id ORDER BY date DESC) as rn
FROM pavement_condition
QUALIFY rn = 1;

-- Grant permissions
GRANT USAGE ON DATABASE DOT_workshop_test TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA smartpave_analytics TO ROLE PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA smartpave_analytics TO ROLE PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA smartpave_analytics TO ROLE PUBLIC;

-- Show completion message
SELECT 'SmartPave Analytics database setup completed successfully!' as status;
