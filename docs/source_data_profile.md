# Source Data Profile

## Dataset selected

- **Dataset:** Superstore Sales
- **Download URL:** https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv
- **Original public reference:** https://github.com/curran/data/tree/gh-pages/superstoreSales
- **Business fit:** Retail-style transactional data with order, customer, product, geography, sales, discount, shipping cost, and profit fields.

## Raw dataset snapshot

- Rows: 8,399
- Columns: 21
- Distinct orders: 5,496
- Distinct customers: 795
- Date range: 2009-01-01 to 2012-12-30
- Product categories: Furniture, Office Supplies, Technology
- Regions: Atlantic, Northwest Territories, Nunavut, Ontario, Prarie, Quebec, West, Yukon

## Notable quality observations

- `Product Base Margin` has 63 missing values and will require imputation logic or nullable handling.
- The CSV contains quoted product names with embedded commas and escaped quotes, so the ETL should use a robust CSV parser rather than naïve string splitting.
- `Order ID` repeats across rows, indicating line-item level granularity rather than one row per order.
- The dataset already includes `Profit`, which supports profitability and margin reporting without separate cost reconstruction.

## Modeling implication

The data naturally supports a **star-schema style reporting layer** centered on a line-item fact table. For portfolio clarity and simpler PostgreSQL loading, this project will implement:

- one cleaned transaction fact table for analytics exports
- optional derived dimensions in SQL views/output files
- KPI logic defined in SQL for dashboard reproducibility
