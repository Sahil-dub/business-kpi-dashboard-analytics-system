CREATE SCHEMA IF NOT EXISTS {{schema}};

CREATE TABLE IF NOT EXISTS {{schema}}.dim_customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    customer_segment VARCHAR(100) NOT NULL,
    first_order_date DATE NOT NULL,
    last_order_date DATE NOT NULL,
    total_orders INTEGER NOT NULL,
    lifetime_revenue NUMERIC(14, 2) NOT NULL,
    lifetime_profit NUMERIC(14, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS {{schema}}.dim_products (
    product_id VARCHAR(32) PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_category VARCHAR(100) NOT NULL,
    product_sub_category VARCHAR(100) NOT NULL,
    product_container VARCHAR(100) NOT NULL,
    typical_unit_price NUMERIC(14, 2),
    average_base_margin NUMERIC(10, 4)
);

CREATE TABLE IF NOT EXISTS {{schema}}.dim_geography (
    geography_id VARCHAR(32) PRIMARY KEY,
    province VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS {{schema}}.fact_sales (
    sales_line_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    order_priority VARCHAR(50) NOT NULL,
    ship_mode VARCHAR(100) NOT NULL,
    customer_id VARCHAR(32) NOT NULL REFERENCES {{schema}}.dim_customers(customer_id),
    geography_id VARCHAR(32) NOT NULL REFERENCES {{schema}}.dim_geography(geography_id),
    product_id VARCHAR(32) NOT NULL REFERENCES {{schema}}.dim_products(product_id),
    customer_type VARCHAR(20) NOT NULL,
    customer_order_number INTEGER NOT NULL,
    first_order_date DATE NOT NULL,
    order_quantity INTEGER NOT NULL,
    sales_amount NUMERIC(14, 2) NOT NULL,
    discount_rate NUMERIC(8, 4) NOT NULL,
    unit_price NUMERIC(14, 2) NOT NULL,
    shipping_cost NUMERIC(14, 2) NOT NULL,
    profit_amount NUMERIC(14, 2) NOT NULL,
    product_base_margin NUMERIC(10, 4),
    gross_margin_pct NUMERIC(10, 2),
    shipping_cost_ratio NUMERIC(10, 2),
    ship_delay_days INTEGER NOT NULL,
    order_sales_total NUMERIC(14, 2) NOT NULL,
    order_profit_total NUMERIC(14, 2) NOT NULL,
    order_line_count INTEGER NOT NULL,
    is_profitable BOOLEAN NOT NULL,
    order_year INTEGER NOT NULL,
    order_quarter INTEGER NOT NULL,
    order_month INTEGER NOT NULL,
    order_month_start DATE NOT NULL,
    order_year_month VARCHAR(7) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_order_date
    ON {{schema}}.fact_sales(order_date);

CREATE INDEX IF NOT EXISTS idx_fact_sales_order_month_start
    ON {{schema}}.fact_sales(order_month_start);

CREATE INDEX IF NOT EXISTS idx_fact_sales_customer_id
    ON {{schema}}.fact_sales(customer_id);

CREATE INDEX IF NOT EXISTS idx_fact_sales_product_id
    ON {{schema}}.fact_sales(product_id);

CREATE INDEX IF NOT EXISTS idx_fact_sales_geography_id
    ON {{schema}}.fact_sales(geography_id);

CREATE INDEX IF NOT EXISTS idx_dim_products_category
    ON {{schema}}.dim_products(product_category, product_sub_category);
