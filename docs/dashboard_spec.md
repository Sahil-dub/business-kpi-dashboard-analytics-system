# Dashboard Specification

## Dashboard goal

Provide leadership with a practical management dashboard for sales, profitability, customer behavior, product performance, and regional performance.

## Recommended Power BI pages

## 1. Executive Overview

### Business story

Show whether the business is growing profitably and whether customer/order performance is healthy at a glance.

### Visuals

- KPI cards: total revenue, total profit, profit margin %, total orders, average order value, repeat customer rate %
- monthly revenue line chart with profit as a secondary tooltip
- revenue by category clustered bar chart
- profit by region map or horizontal bar chart

### Slicers

- order year
- region
- customer segment
- product category

### Recommended measures

- `Total Revenue = SUM(cleaned_dataset[sales_amount])`
- `Total Profit = SUM(cleaned_dataset[profit_amount])`
- `Profit Margin % = DIVIDE([Total Profit], [Total Revenue])`
- `Total Orders = DISTINCTCOUNT(cleaned_dataset[order_id])`
- `Average Order Value = DIVIDE([Total Revenue], [Total Orders])`
- `Repeat Customer Rate % = DIVIDE(DISTINCTCOUNT(FILTER(cleaned_dataset, cleaned_dataset[customer_type] = "Repeat")[customer_id]), DISTINCTCOUNT(cleaned_dataset[customer_id]))`

## 2. Sales Trends

### Business story

Explain seasonality, trend changes, and whether revenue growth is translating into better profit.

### Visuals

- monthly revenue trend line chart
- month-over-month growth column chart
- revenue and profit by year combo chart
- order count by month heatmap or matrix

### Slicers

- year
- product category
- customer segment

### Recommended measures

- `MoM Revenue Growth %`
- `Monthly Orders`
- `Monthly Profit`

## 3. Customer Insights

### Business story

Show who buys most often, which segments drive value, and how much revenue depends on repeat customers.

### Visuals

- stacked bar: revenue by customer segment and customer type
- table: top customers by revenue and profit
- donut chart: one-time vs repeat customers
- scatter plot: customers by orders vs profit

### Slicers

- customer segment
- region
- year

### Recommended measures

- customer lifetime revenue
- customer lifetime profit
- orders per customer
- repeat customer count

## 4. Product and Category Performance

### Business story

Identify high-revenue winners, high-margin winners, and categories that look strong on sales but weak on profit.

### Visuals

- top 10 products by revenue bar chart
- category/sub-category revenue and profit matrix
- bubble chart: revenue vs profit by product
- bottom 10 products by profit table

### Slicers

- product category
- product sub-category
- region

### Recommended measures

- revenue by product
- profit by product
- profit margin by sub-category
- quantity sold

## 5. Regional Performance

### Business story

Help management compare provinces and regions on both sales scale and profitability quality.

### Visuals

- filled map or shape map by province
- horizontal bar chart for revenue by region/province
- profit margin by region column chart
- table of orders, customers, revenue, and profit by geography

### Slicers

- year
- product category
- customer segment

## Layout guidance

- Use a 16:9 canvas and keep the Executive Overview as the landing page.
- Keep KPI cards across the top row.
- Place time-series visuals on the left and ranking visuals on the right.
- Use a consistent color story: revenue in blue, profit in green, loss or low margin in orange/red.
- Add tooltip pages for product and customer drill-downs if extra polish is needed.

## Data model guidance

For a simple Power BI build, load `outputs/cleaned_dataset.csv` as the main fact-style table and create calculated measures directly in Power BI.

For a more production-style version, load:

- `outputs/kpi_summary.csv`
- `outputs/monthly_revenue.csv`
- `outputs/top_products.csv`
- `outputs/top_categories.csv`
- `outputs/top_regions.csv`
- `outputs/customer_segments.csv`
- `outputs/customer_summary.csv`

This gives a fast portfolio demo path even without a live PostgreSQL connection.
