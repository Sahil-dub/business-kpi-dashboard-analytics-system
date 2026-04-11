# Business KPI Dashboard & Analytics System

Portfolio-ready analytics engineering project for a retail-style business. The repository shows how to take a messy public sales dataset from raw CSV to cleaned reporting tables, KPI outputs, a PostgreSQL-ready schema, and a Power BI dashboard specification.

## Project overview

This project simulates a management reporting system for a retail / e-commerce business that needs visibility into:

- revenue and profitability
- order trends over time
- customer behavior and repeat purchasing
- product and category performance
- regional performance

The final output is designed to be useful both as a technical portfolio project and as a practical BI reporting case study.

## Business problem

Leadership teams often have transactional sales data but no consistent analytics layer. That creates several problems:

- KPIs are recalculated differently across teams
- profitability issues hide behind headline revenue
- customer retention is hard to monitor
- product and regional underperformance are spotted too late

This repository solves that by building a reproducible pipeline that cleans the data, prepares a reporting schema, exports KPI files, and documents the dashboard design.

## Dataset

- Dataset: Superstore Sales
- Raw file: `data/raw/superstore_sales.csv`
- Public source: [curran/data superstoreSales](https://github.com/curran/data/tree/gh-pages/superstoreSales)
- Direct CSV URL: [superstoreSales.csv](https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv)

Why this dataset was chosen:

- transactional retail-style structure
- includes sales, profit, discount, quantity, shipping, category, and region fields
- supports revenue, margin, customer, and regional KPI reporting

## Architecture

`Raw CSV -> Python ETL -> Cleaned dataset -> PostgreSQL star schema -> SQL KPIs -> Power BI-ready outputs`

See [architecture.md](docs/architecture.md) for the full explanation.

## Tech stack

- Python 3.11
- pandas
- numpy
- SQLAlchemy
- psycopg2-binary
- PostgreSQL
- pytest
- matplotlib
- Markdown
- Git

## Repository structure

```text
.
|-- README.md
|-- requirements.txt
|-- .env.example
|-- data/
|   |-- raw/
|   |   `-- superstore_sales.csv
|   `-- processed/
|       `-- cleaned_sales_dataset.csv
|-- docs/
|   |-- architecture.md
|   |-- business_insights.md
|   |-- dashboard_spec.md
|   `-- source_data_profile.md
|-- outputs/
|   |-- cleaned_dataset.csv
|   |-- customer_segments.csv
|   |-- customer_summary.csv
|   |-- kpi_summary.csv
|   |-- low_performing_products.csv
|   |-- monthly_revenue.csv
|   |-- top_categories.csv
|   |-- top_products.csv
|   |-- top_regions.csv
|   `-- charts/
|       |-- category_profitability.png
|       `-- monthly_revenue_trend.png
|-- sql/
|   |-- kpi_queries.sql
|   `-- schema.sql
|-- src/
|   |-- analysis.py
|   |-- config.py
|   |-- extract.py
|   |-- load.py
|   |-- pipeline.py
|   `-- transform.py
`-- tests/
    `-- test_transform.py
```

## Data model

The reporting model uses a star-schema approach:

- `dim_customers`
- `dim_products`
- `dim_geography`
- `fact_sales`

This was chosen because it is:

- easy to explain in interviews
- practical for KPI queries
- friendly for Power BI relationships

## Key outputs

Current generated KPI highlights:

- Total revenue: **$14.92M**
- Total profit: **$1.52M**
- Profit margin: **10.2%**
- Total orders: **5,496**
- Total customers: **795**
- Average order value: **$2,713.90**
- Repeat customers: **784**
- One-time customers: **11**
- Repeat customer rate: **98.62%**

More business interpretation is documented in [business_insights.md](docs/business_insights.md).

## Setup instructions

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure PostgreSQL credentials

Copy `.env.example` to `.env` and set:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_SCHEMA`

If `POSTGRES_PASSWORD` is not set, the pipeline still runs and generates all CSV outputs, but skips the database load step.

## How to run the ETL pipeline

```powershell
python -m src.pipeline
```

What the pipeline does:

1. reads the raw CSV
2. standardizes and cleans the data
3. engineers reporting columns
4. writes the cleaned dataset to `data/processed/` and `outputs/`
5. generates KPI CSV files and chart assets
6. loads PostgreSQL tables when credentials are configured

## How to initialize PostgreSQL

### Option 1: let the pipeline create and load tables

```powershell
python -m src.pipeline
```

### Option 2: run the schema manually first

```sql
-- Replace {{schema}} with your schema name, for example analytics,
-- then run the resulting SQL in PostgreSQL.
```

Then load with the Python pipeline.

## How to run tests

```powershell
pytest tests/test_transform.py
```

## SQL KPI coverage

`sql/kpi_queries.sql` contains SQL for:

- KPI summary
- monthly revenue and MoM growth
- top products
- top categories
- top regions
- customer retention
- low-performing products

## Power BI dashboard overview

The repository includes a full dashboard build guide in [dashboard_spec.md](docs/dashboard_spec.md).

Recommended report pages:

- Executive Overview
- Sales Trends
- Customer Insights
- Product and Category Performance
- Regional Performance

The fastest Power BI path is to load `outputs/cleaned_dataset.csv` and create DAX measures from the cleaned fact-style export.

## Example deliverables created

- cleaned transaction dataset
- star schema DDL
- SQL KPI query pack
- chart assets for reporting
- business insights write-up
- dashboard specification

## Portfolio value

This project is suitable for applications to:

- Data Analyst internships
- BI Analyst roles
- Reporting Analyst roles
- Working Student data roles
- Digitalization roles with reporting focus

It demonstrates:

- practical ETL engineering
- SQL KPI design
- production-friendly project structure
- data storytelling
- BI handoff readiness

## Resume usage ideas

- Built an end-to-end retail analytics pipeline in Python and SQL, transforming raw transactional sales data into Power BI-ready KPI datasets and a PostgreSQL reporting model.
- Designed a star-schema analytics database and KPI query pack covering revenue, profitability, customer retention, product performance, and regional reporting.
- Produced business-facing documentation and dashboard specifications that translated computed metrics into management-ready insights.

## Future improvements

- add dbt models for warehouse-style transformations
- add orchestration with a lightweight scheduler
- add data quality assertions beyond the current unit test
- publish a `.pbix` file or Power BI screenshots
- containerize PostgreSQL + pipeline execution with Docker

## Notes and limitations

- The dataset uses customer names rather than a native customer ID, so surrogate customer keys are generated during transformation.
- PostgreSQL loading is implemented but requires local database credentials.
- The project currently exports dashboard-ready CSVs instead of a committed `.pbix` file.
