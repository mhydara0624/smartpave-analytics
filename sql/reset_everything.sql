-- SmartPave Analytics: Complete Reset Script
-- WARNING: This will delete EVERYTHING - use with caution!

-- Drop the entire database (this removes everything)
DROP DATABASE IF EXISTS DOT_workshop_test;

-- Show reset status
SELECT 'Complete reset completed successfully!' as status;
SELECT 'Database DOT_workshop_test has been completely removed.' as message;
SELECT 'Run setup_database.sql to start completely fresh.' as next_step;
