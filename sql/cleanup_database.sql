-- SmartPave Analytics: Database Cleanup Script
-- Run this to completely remove all tables and data for fresh testing

USE DATABASE DOT_workshop_test;
USE SCHEMA smartpave_analytics;

-- Drop all tables in reverse dependency order
DROP TABLE IF EXISTS optimization_results;
DROP TABLE IF EXISTS model_results;
DROP TABLE IF EXISTS pavement_features;
DROP TABLE IF EXISTS traffic_data;
DROP TABLE IF EXISTS maintenance_records;
DROP TABLE IF EXISTS pavement_condition;
DROP TABLE IF EXISTS road_network;

-- Drop all views
DROP VIEW IF EXISTS current_conditions;
DROP VIEW IF EXISTS pavement_analysis;

-- Drop all stages
DROP STAGE IF EXISTS @smartpave_stage/raw/;
DROP STAGE IF EXISTS @smartpave_stage/processed/;
DROP STAGE IF EXISTS @smartpave_stage/models/;

-- Optional: Drop the entire schema (uncomment if you want to start completely fresh)
-- DROP SCHEMA IF EXISTS smartpave_analytics;

-- Optional: Drop the entire database (uncomment if you want to start completely fresh)
-- DROP DATABASE IF EXISTS DOT_workshop_test;

-- Show cleanup status
SELECT 'SmartPave Analytics cleanup completed successfully!' as status;
SELECT 'All tables, views, and stages have been removed.' as message;
SELECT 'You can now run setup_database.sql to start fresh.' as next_step;
