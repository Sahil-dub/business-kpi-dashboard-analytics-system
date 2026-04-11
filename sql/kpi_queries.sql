-- name: kpi_summary
WITH order_summary AS (
    SELECT
        order_id,
        SUM(sales_amount) AS order_revenue,
        SUM(profit_amount) AS order_profit
    FROM {{schema}}.fact_sales
    GROUP BY order_id
),
customer_rollup AS (
    SELECT
        COUNT(DISTINCT customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN customer_type = 'Repeat' THEN customer_id END) AS repeat_customers
    FROM {{schema}}.fact_sales
)
SELECT 'total_revenue' AS metric, ROUND(SUM(sales_amount)::numeric, 2)::text AS value
FROM {{schema}}.fact_sales
UNION ALL
SELECT 'total_profit', ROUND(SUM(profit_amount)::numeric, 2)::text
FROM {{schema}}.fact_sales
UNION ALL
SELECT 'profit_margin_pct', ROUND((SUM(profit_amount) / NULLIF(SUM(sales_amount), 0) * 100)::numeric, 2)::text
FROM {{schema}}.fact_sales
UNION ALL
SELECT 'total_orders', COUNT(DISTINCT order_id)::text
FROM {{schema}}.fact_sales
UNION ALL
SELECT 'average_order_value', ROUND(AVG(order_revenue)::numeric, 2)::text
FROM order_summary
UNION ALL
SELECT 'total_customers', total_customers::text
FROM customer_rollup
UNION ALL
SELECT 'repeat_customers', repeat_customers::text
FROM customer_rollup
UNION ALL
SELECT 'one_time_customers', (total_customers - repeat_customers)::text
FROM customer_rollup
UNION ALL
SELECT 'repeat_customer_rate_pct', ROUND((repeat_customers::numeric / NULLIF(total_customers, 0) * 100), 2)::text
FROM customer_rollup;

-- name: monthly_revenue
WITH monthly_base AS (
    SELECT
        order_month_start,
        SUM(sales_amount) AS revenue,
        SUM(profit_amount) AS profit,
        COUNT(DISTINCT order_id) AS orders,
        COUNT(DISTINCT customer_id) AS customers
    FROM {{schema}}.fact_sales
    GROUP BY order_month_start
)
SELECT
    order_month_start,
    ROUND(revenue::numeric, 2) AS revenue,
    ROUND(profit::numeric, 2) AS profit,
    orders,
    customers,
    ROUND((revenue / NULLIF(orders, 0))::numeric, 2) AS average_order_value,
    ROUND(
        (
            (revenue - LAG(revenue) OVER (ORDER BY order_month_start)) /
            NULLIF(LAG(revenue) OVER (ORDER BY order_month_start), 0)
        )::numeric * 100,
        2
    ) AS mom_revenue_growth_pct
FROM monthly_base
ORDER BY order_month_start;

-- name: top_products
SELECT
    p.product_name,
    p.product_category,
    ROUND(SUM(f.sales_amount)::numeric, 2) AS revenue,
    ROUND(SUM(f.profit_amount)::numeric, 2) AS profit,
    SUM(f.order_quantity) AS quantity,
    COUNT(DISTINCT f.order_id) AS orders,
    ROUND((SUM(f.profit_amount) / NULLIF(SUM(f.sales_amount), 0) * 100)::numeric, 2) AS profit_margin_pct
FROM {{schema}}.fact_sales f
JOIN {{schema}}.dim_products p
    ON f.product_id = p.product_id
GROUP BY p.product_name, p.product_category
ORDER BY revenue DESC, profit DESC
LIMIT 10;

-- name: top_categories
SELECT
    p.product_category,
    p.product_sub_category,
    ROUND(SUM(f.sales_amount)::numeric, 2) AS revenue,
    ROUND(SUM(f.profit_amount)::numeric, 2) AS profit,
    SUM(f.order_quantity) AS quantity,
    COUNT(DISTINCT f.order_id) AS orders,
    ROUND((SUM(f.profit_amount) / NULLIF(SUM(f.sales_amount), 0) * 100)::numeric, 2) AS profit_margin_pct
FROM {{schema}}.fact_sales f
JOIN {{schema}}.dim_products p
    ON f.product_id = p.product_id
GROUP BY p.product_category, p.product_sub_category
ORDER BY revenue DESC, profit DESC;

-- name: top_regions
SELECT
    g.region,
    g.province,
    ROUND(SUM(f.sales_amount)::numeric, 2) AS revenue,
    ROUND(SUM(f.profit_amount)::numeric, 2) AS profit,
    COUNT(DISTINCT f.order_id) AS orders,
    COUNT(DISTINCT f.customer_id) AS customers,
    ROUND((SUM(f.profit_amount) / NULLIF(SUM(f.sales_amount), 0) * 100)::numeric, 2) AS profit_margin_pct
FROM {{schema}}.fact_sales f
JOIN {{schema}}.dim_geography g
    ON f.geography_id = g.geography_id
GROUP BY g.region, g.province
ORDER BY revenue DESC, profit DESC;

-- name: customer_retention
SELECT
    customer_type,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(sales_amount)::numeric, 2) AS revenue,
    ROUND(SUM(profit_amount)::numeric, 2) AS profit,
    COUNT(DISTINCT order_id) AS orders,
    ROUND((SUM(sales_amount) / NULLIF(COUNT(DISTINCT order_id), 0))::numeric, 2) AS average_order_value
FROM {{schema}}.fact_sales
GROUP BY customer_type
ORDER BY revenue DESC;

-- name: low_performing_products
SELECT
    p.product_name,
    p.product_category,
    ROUND(SUM(f.sales_amount)::numeric, 2) AS revenue,
    ROUND(SUM(f.profit_amount)::numeric, 2) AS profit,
    SUM(f.order_quantity) AS quantity,
    COUNT(DISTINCT f.order_id) AS orders,
    ROUND((SUM(f.profit_amount) / NULLIF(SUM(f.sales_amount), 0) * 100)::numeric, 2) AS profit_margin_pct
FROM {{schema}}.fact_sales f
JOIN {{schema}}.dim_products p
    ON f.product_id = p.product_id
GROUP BY p.product_name, p.product_category
HAVING COUNT(DISTINCT f.order_id) >= 3
ORDER BY profit ASC, profit_margin_pct ASC, revenue DESC
LIMIT 10;
