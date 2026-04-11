"""Database loading utilities for PostgreSQL."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import Settings


def create_engine_from_settings(settings: Settings) -> Engine:
    return create_engine(settings.database_url, future=True)


def execute_sql_file(engine: Engine, sql_path: Path, schema_name: str) -> None:
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

    fact_sales = clean_df.copy().rename(columns={"row_id": "sales_line_id"})

    return {
        "dim_customers": customers,
        "dim_products": products,
        "dim_geography": geography,
        "fact_sales": fact_sales,
    }


def load_to_postgres(clean_df: pd.DataFrame, settings: Settings) -> None:
    """Create the schema and load dimension/fact tables into PostgreSQL."""

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
