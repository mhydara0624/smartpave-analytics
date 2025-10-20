-- SmartPave Analytics: Data Loading Script
-- Run this after setup_database.sql to load all data into Snowflake tables

USE DATABASE DOT_workshop_test;
USE SCHEMA smartpave_analytics;

-- Upload data files to stages (run these commands from SnowSQL or Snowsight)
-- PUT file://data/raw/road_network.csv @smartpave_stage/;
-- PUT file://data/raw/pavement_condition_2020-2024.csv @smartpave_stage/;
-- PUT file://data/raw/maintenance_records_2020-2024.csv @smartpave_stage/;
-- PUT file://data/raw/traffic_volume_data.csv @smartpave_stage/;

-- Load road network data
COPY INTO road_network
FROM @smartpave_stage/road_network.csv
FILE_FORMAT = (FORMAT_NAME = csv_format)
ON_ERROR = 'CONTINUE';

-- Load pavement condition data
COPY INTO pavement_condition
FROM @smartpave_stage/pavement_condition_2020-2024.csv
FILE_FORMAT = (FORMAT_NAME = csv_format)
ON_ERROR = 'CONTINUE';

-- Load maintenance records data
COPY INTO maintenance_records
FROM @smartpave_stage/maintenance_records_2020-2024.csv
FILE_FORMAT = (FORMAT_NAME = csv_format)
ON_ERROR = 'CONTINUE';

-- Load traffic data
COPY INTO traffic_data
FROM @smartpave_stage/traffic_volume_data.csv
FILE_FORMAT = (FORMAT_NAME = csv_format)
ON_ERROR = 'CONTINUE';

-- Verify data loading
SELECT 'Road Network' as table_name, COUNT(*) as record_count FROM road_network
UNION ALL
SELECT 'Pavement Condition' as table_name, COUNT(*) as record_count FROM pavement_condition
UNION ALL
SELECT 'Maintenance Records' as table_name, COUNT(*) as record_count FROM maintenance_records
UNION ALL
SELECT 'Traffic Data' as table_name, COUNT(*) as record_count FROM traffic_data;

-- Show sample data
SELECT 'Sample Road Network Data:' as info;
SELECT * FROM road_network LIMIT 5;

SELECT 'Sample Pavement Condition Data:' as info;
SELECT * FROM pavement_condition LIMIT 5;

SELECT 'Sample Maintenance Records:' as info;
SELECT * FROM maintenance_records LIMIT 5;

-- Create summary statistics
SELECT 
    'Data Loading Summary' as summary,
    (SELECT COUNT(*) FROM road_network) as road_segments,
    (SELECT COUNT(*) FROM pavement_condition) as condition_records,
    (SELECT COUNT(*) FROM maintenance_records) as maintenance_records,
    (SELECT COUNT(*) FROM traffic_data) as traffic_records,
    (SELECT SUM(cost) FROM maintenance_records) as total_maintenance_cost,
    (SELECT AVG(condition_score) FROM pavement_condition) as avg_condition_score;
