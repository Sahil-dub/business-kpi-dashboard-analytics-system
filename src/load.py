"""Database loading utilities for PostgreSQL."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from src.config import Settings

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


def create_engine_from_settings(settings: Settings) -> "Engine":
    from sqlalchemy import create_engine

    return create_engine(settings.database_url, future=True)


def execute_sql_file(engine: "Engine", sql_path: Path, schema_name: str) -> None:
    from sqlalchemy import text

    sql_text = sql_path.read_text(encoding="utf-8").replace("{{schema}}", schema_name)
    statements = [statement.strip() for statement in sql_text.split(";") if statement.strip()]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def build_dimension_tables(clean_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    customers = (
        clean_df.groupby(["customer_id", "customer_name", "customer_segment"], as_index=False)
        .agg(
            first_order_date=("first_order_date", "min"),
            last_order_date=("order_date", "max"),
            total_orders=("order_id", "nunique"),
            lifetime_revenue=("sales_amount", "sum"),
            lifetime_profit=("profit_amount", "sum"),
        )
        .round({"lifetime_revenue": 2, "lifetime_profit": 2})
    )

    products = (
        clean_df.groupby(
            [
                "product_id",
                "product_name",
                "product_category",
                "product_sub_category",
                "product_container",
            ],
            as_index=False,
        )
        .agg(
            typical_unit_price=("unit_price", "median"),
            average_base_margin=("product_base_margin", "median"),
        )
        .round(2)
    )

    geography = clean_df[["geography_id", "province", "region"]].drop_duplicates().reset_index(
        drop=True
    )

    fact_sales = clean_df.rename(columns={"row_id": "sales_line_id"})[
        [
            "sales_line_id",
            "order_id",
            "order_date",
            "ship_date",
            "order_priority",
            "ship_mode",
            "customer_id",
            "geography_id",
            "product_id",
            "customer_type",
            "customer_order_number",
            "first_order_date",
            "order_quantity",
            "sales_amount",
            "discount_rate",
            "unit_price",
            "shipping_cost",
            "profit_amount",
            "product_base_margin",
            "gross_margin_pct",
            "shipping_cost_ratio",
            "ship_delay_days",
            "order_sales_total",
            "order_profit_total",
            "order_line_count",
            "is_profitable",
            "order_year",
            "order_quarter",
            "order_month",
            "order_month_start",
            "order_year_month",
        ]
    ].copy()

    return {
        "dim_customers": customers,
        "dim_products": products,
        "dim_geography": geography,
        "fact_sales": fact_sales,
    }


def load_to_postgres(clean_df: pd.DataFrame, settings: Settings) -> None:
    """Create the schema and load dimension/fact tables into PostgreSQL."""

    from sqlalchemy import text

    engine = create_engine_from_settings(settings)
    execute_sql_file(engine, settings.sql_dir / "schema.sql", settings.postgres_schema)
    tables = build_dimension_tables(clean_df)

    with engine.begin() as connection:
        connection.execute(
            text(
                f"TRUNCATE TABLE {settings.postgres_schema}.fact_sales "
                "RESTART IDENTITY CASCADE"
            )
        )
        connection.execute(
            text(
                f"TRUNCATE TABLE {settings.postgres_schema}.dim_products "
                "RESTART IDENTITY CASCADE"
            )
        )
        connection.execute(
            text(
                f"TRUNCATE TABLE {settings.postgres_schema}.dim_customers "
                "RESTART IDENTITY CASCADE"
            )
        )
        connection.execute(
            text(
                f"TRUNCATE TABLE {settings.postgres_schema}.dim_geography "
                "RESTART IDENTITY CASCADE"
            )
        )

    for table_name in ["dim_customers", "dim_products", "dim_geography", "fact_sales"]:
        tables[table_name].to_sql(
            name=table_name,
            con=engine,
            schema=settings.postgres_schema,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )
