# Architecture

## System flow

`Raw CSV -> Python ETL -> Cleaned analytics table -> PostgreSQL star schema -> SQL KPI queries -> Power BI-ready CSV exports`

## Components

### 1. Raw data layer

- Source file: `data/raw/superstore_sales.csv`
- Granularity: one row per order line item
- Coverage: 2009-01-01 to 2012-12-30

### 2. Python ETL layer

Pipeline entrypoint: `python -m src.pipeline`

Core modules:

- `src/extract.py`: reads the raw CSV using a parser setup that handles quoted commas and Latin-1 characters
- `src/transform.py`: cleans the dataset, standardizes columns, fixes data types, imputes `product_base_margin`, and engineers reporting fields such as `customer_type`, `gross_margin_pct`, and `order_month_start`
- `src/analysis.py`: generates KPI exports and chart assets for downstream dashboarding
- `src/load.py`: creates and loads a PostgreSQL star schema when database credentials are configured

### 3. Storage layer

Two storage targets are supported:

- `data/processed/cleaned_sales_dataset.csv`: the canonical cleaned flat file for analysis and dashboard prototyping
- PostgreSQL schema `analytics` by default: the production-style reporting model

### 4. Reporting layer

SQL KPIs are stored in `sql/kpi_queries.sql` and cover:

- executive KPI cards
- monthly revenue and month-over-month growth
- product and category performance
- regional performance
- repeat customer analysis
- low-performing products

### 5. Power BI handoff

The `outputs/` folder contains dashboard-ready CSV files:

- `cleaned_dataset.csv`
- `kpi_summary.csv`
- `monthly_revenue.csv`
- `top_products.csv`
- `top_categories.csv`
- `top_regions.csv`
- `customer_segments.csv`
- `customer_summary.csv`
- `low_performing_products.csv`

## Schema design rationale

The source data is transactional and naturally fits a star-schema reporting model. This project uses:

- `dim_customers`: customer attributes and lifetime metrics
- `dim_products`: product hierarchy and price/margin descriptors
- `dim_geography`: province and region attributes
- `fact_sales`: order-line facts for revenue, quantity, shipping, profit, and customer behavior

This design was chosen because it is easy to explain in interviews, efficient for KPI queries, and practical for Power BI relationships.
