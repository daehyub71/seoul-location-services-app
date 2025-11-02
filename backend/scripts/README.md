# Scripts Directory

This directory contains utility scripts for data collection, database initialization, and maintenance.

## Database Setup

### init_supabase_schema.sql
Creates all database tables, indexes, and helper functions in Supabase.

**Usage:**
1. Open Supabase Dashboard → SQL Editor
2. Copy and paste the contents of `init_supabase_schema.sql`
3. Click "Run" to execute

This will create:
- 5 main tables (cultural_events, libraries, cultural_spaces, public_reservations, future_heritages)
- 1 logging table (collection_logs)
- PostGIS spatial indexes
- Helper functions for proximity queries
- Triggers for auto-updating location fields

## Data Collection Scripts

(Will be created in Day 3-6)

- `collect_data.py` - Main data collection orchestrator
- `collect_all.py` - Collect all data from all APIs
- `scheduler.py` - APScheduler for automated collection
- `data_quality_check.py` - Validate collected data

## Database Initialization

(Will be created in Day 2)

- `init_db.py` - Initialize database connection and verify schema

## Usage Examples

```bash
# Initialize database schema (run in Supabase SQL Editor)
# Copy contents of init_supabase_schema.sql

# Collect all data (Day 6+)
python scripts/collect_all.py

# Run scheduler for automated collection (Day 6+)
python scripts/scheduler.py

# Check data quality (Day 7)
python scripts/data_quality_check.py
```
