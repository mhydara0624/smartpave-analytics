# SmartPave Analytics: Snowflake Execution Guide

## 🚨 **Important: Snowflake Notebook Limitations**

### **Key Limitations:**
1. **No persistent state** between notebooks
2. **No file system access** (can't read local CSV files)
3. **Each notebook must be self-contained**
4. **Data must be in Snowflake tables or stages**

## 🚀 **Execution Steps**

### **Step 1: Setup Database (Run Once)**
```sql
-- Run in Snowsight SQL editor
-- File: sql/setup_database.sql
CREATE DATABASE IF NOT EXISTS DOT_workshop_test;
USE DATABASE DOT_workshop_test;
CREATE SCHEMA IF NOT EXISTS smartpave_analytics;
USE SCHEMA smartpave_analytics;
-- ... (rest of setup_database.sql)
```

### **Step 2: Upload Data Files**
```sql
-- Upload CSV files to Snowflake stages
PUT file://data/raw/road_network.csv @smartpave_stage/raw/;
PUT file://data/raw/pavement_condition_2020-2024.csv @smartpave_stage/raw/;
PUT file://data/raw/maintenance_records_2020-2024.csv @smartpave_stage/raw/;
PUT file://data/raw/traffic_volume_data.csv @smartpave_stage/raw/;
```

### **Step 3: Load Data into Tables**
```sql
-- Run in Snowsight SQL editor
-- File: sql/load_data.sql
COPY INTO road_network FROM @smartpave_stage/raw/road_network.csv ...;
COPY INTO pavement_condition FROM @smartpave_stage/raw/pavement_condition_2020-2024.csv ...;
-- ... (rest of load_data.sql)
```

### **Step 4: Run Notebooks Sequentially**

#### **Notebook 1: Data Exploration**
- **Loads from**: `pavement_condition`, `maintenance_records`, `road_network`, `traffic_data` tables
- **Saves to**: Nothing (exploration only)
- **Key changes**: Uses `session.sql()` instead of `pd.read_csv()`

#### **Notebook 2: Feature Engineering**
- **Loads from**: `pavement_condition`, `maintenance_records` tables
- **Saves to**: `pavement_features` table
- **Key changes**: Creates features and saves to new table

```python
# Example: Save features to Snowflake table
features_df.to_sql('pavement_features', session, if_exists='replace', index=False)
```

#### **Notebook 3: ML Modeling**
- **Loads from**: `pavement_features` table
- **Saves to**: `model_results` table + model files to stage
- **Key changes**: Saves models to Snowflake stage

```python
# Example: Save model to Snowflake stage
import joblib
joblib.dump(model, '/tmp/model.pkl')
session.file.put('/tmp/model.pkl', '@smartpave_stage/models/')
```

#### **Notebook 4: Cost Optimization**
- **Loads from**: `pavement_features`, `model_results` tables
- **Saves to**: `optimization_results` table
- **Key changes**: Saves optimization results to table

#### **Notebook 5: Visualization Dashboard**
- **Loads from**: All tables (`pavement_analysis` view)
- **Saves to**: Nothing (visualization only)
- **Key changes**: Uses Snowflake views for final analysis

## 📊 **Data Flow in Snowflake**

```
CSV Files → Stages → Tables → Features → Models → Results
    ↓         ↓        ↓         ↓         ↓        ↓
Raw Data → Upload → Load → Process → Train → Optimize
```

## 🔧 **Key Code Changes for Snowflake**

### **Data Loading**
```python
# OLD (won't work in Snowflake)
df = pd.read_csv('../data/raw/data.csv')

# NEW (Snowflake compatible)
from snowflake.snowpark.context import get_active_session
session = get_active_session()
df = session.sql("SELECT * FROM table_name").to_pandas()
```

### **Data Saving**
```python
# OLD (won't work in Snowflake)
df.to_csv('../data/processed/features.csv')

# NEW (Snowflake compatible)
df.to_sql('table_name', session, if_exists='replace', index=False)
```

### **Model Saving**
```python
# OLD (won't work in Snowflake)
joblib.dump(model, '../models/model.pkl')

# NEW (Snowflake compatible)
joblib.dump(model, '/tmp/model.pkl')
session.file.put('/tmp/model.pkl', '@smartpave_stage/models/')
```

## 📁 **Updated Project Structure**

```
smartpave-analytics/
├── data/
│   └── raw/                    # CSV files for upload to Snowflake
├── sql/                        # SQL setup scripts
│   ├── setup_database.sql      # Create tables and views
│   └── load_data.sql          # Load data from stages to tables
├── notebooks/                  # Snowflake-compatible notebooks
│   ├── 1-data-exploration.ipynb
│   ├── 2-feature-engineering.ipynb
│   ├── 3-ml-modeling.ipynb
│   ├── 4-cost-optimization.ipynb
│   └── 5-visualization-dashboard.ipynb
└── models/                     # Empty - models saved to Snowflake stages
```

## ⚠️ **Common Issues & Solutions**

### **Issue 1: "Table doesn't exist"**
**Solution**: Run `setup_database.sql` first

### **Issue 2: "No data in tables"**
**Solution**: Run `load_data.sql` after uploading files

### **Issue 3: "Can't read CSV files"**
**Solution**: Use Snowflake tables instead of local files

### **Issue 4: "Variables not available"**
**Solution**: Each notebook must load its own data from tables

## 🎯 **Workshop Demo Flow**

### **Phase 1: Setup (10 min)**
1. Show database setup
2. Upload data files
3. Load data into tables
4. Verify data loading

### **Phase 2: Analysis (35 min)**
1. **Notebook 1** (5 min): Data exploration
2. **Notebook 2** (10 min): Feature engineering
3. **Notebook 3** (10 min): ML modeling
4. **Notebook 4** (5 min): Cost optimization
5. **Notebook 5** (5 min): Visualization

### **Phase 3: Results (5 min)**
1. Show final dashboards
2. Demonstrate cost savings
3. Highlight performance gains

## 💡 **Pro Tips**

1. **Always check table exists** before loading data
2. **Use views** for complex queries across tables
3. **Save intermediate results** to tables for next notebook
4. **Use stages** for file storage (models, exports)
5. **Test each notebook independently** before running sequence

## 🚀 **Quick Start Commands**

```sql
-- 1. Setup (run once)
@sql/setup_database.sql

-- 2. Upload files (run once)
PUT file://data/raw/*.csv @smartpave_stage/raw/;

-- 3. Load data (run once)
@sql/load_data.sql

-- 4. Run notebooks in Snowflake Notebooks interface
-- Each notebook is self-contained and loads from tables
```

**This approach ensures all notebooks work independently in Snowflake while maintaining the complete data science workflow!**
