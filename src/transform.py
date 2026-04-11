"""Cleaning and transformation logic for the sales dataset."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd


def _to_snake_case(column_name: str) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", column_name.strip())
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    return normalized.strip("_").lower()


def _create_surrogate_ids(series: pd.Series, prefix: str) -> pd.Series:
    cleaned = series.fillna("Unknown").astype(str).str.strip()
    codes = pd.factorize(cleaned, sort=True)[0] + 1
    return pd.Series([f"{prefix}-{code:04d}" for code in codes], index=series.index)


def clean_sales_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw line-item dataset and engineer reporting fields."""

    df = raw_df.copy()
    df.columns = [_to_snake_case(column) for column in df.columns]

    df = df.rename(
        columns={
            "sales": "sales_amount",
            "discount": "discount_rate",
            "profit": "profit_amount",
        }
    )

    string_columns = [
        "order_priority",
        "ship_mode",
        "customer_name",
        "province",
        "region",
        "customer_segment",
        "product_category",
        "product_sub_category",
        "product_name",
        "product_container",
    ]
    for column in string_columns:
        df[column] = df[column].astype(str).str.strip()

    numeric_columns = [
        "row_id",
        "order_id",
        "order_quantity",
        "sales_amount",
        "discount_rate",
        "profit_amount",
        "unit_price",
        "shipping_cost",
        "product_base_margin",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    for column in ["order_date", "ship_date"]:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    df = df.drop_duplicates().reset_index(drop=True)
    df = df.dropna(
        subset=[
            "order_id",
            "order_date",
            "customer_name",
            "product_name",
            "product_category",
            "region",
            "sales_amount",
            "profit_amount",
        ]
    )

    df = df[df["order_quantity"].fillna(0) > 0].copy()
    df = df[df["sales_amount"].fillna(0) >= 0].copy()

    subgroup_margin = (
        df.groupby("product_sub_category")["product_base_margin"].transform("median")
    )
    overall_margin = df["product_base_margin"].median()
    df["product_base_margin"] = df["product_base_margin"].fillna(subgroup_margin)
    df["product_base_margin"] = df["product_base_margin"].fillna(overall_margin)

    df["customer_id"] = _create_surrogate_ids(
        df["customer_name"].astype(str) + "|" + df["customer_segment"].astype(str),
        prefix="CUST",
    )
    df["product_id"] = _create_surrogate_ids(df["product_name"], prefix="PROD")
    df["geography_id"] = _create_surrogate_ids(
        df["region"].astype(str) + "|" + df["province"].astype(str), prefix="GEO"
    )

    df["ship_delay_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["ship_delay_days"] = df["ship_delay_days"].fillna(0).clip(lower=0)

    df["gross_margin_pct"] = np.where(
        df["sales_amount"] != 0,
        (df["profit_amount"] / df["sales_amount"]) * 100,
        0,
    )
    df["shipping_cost_ratio"] = np.where(
        df["sales_amount"] != 0,
        (df["shipping_cost"] / df["sales_amount"]) * 100,
        0,
    )
    df["is_profitable"] = df["profit_amount"] > 0

    df["order_year"] = df["order_date"].dt.year.astype(int)
    df["order_quarter"] = df["order_date"].dt.quarter.astype(int)
    df["order_month"] = df["order_date"].dt.month.astype(int)
    df["order_month_start"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["order_year_month"] = df["order_date"].dt.strftime("%Y-%m")

    customer_orders = (
        df[["customer_id", "order_id", "order_date"]]
        .drop_duplicates()
        .sort_values(["customer_id", "order_date", "order_id"])
        .copy()
    )
    customer_orders["customer_order_number"] = (
        customer_orders.groupby("customer_id").cumcount() + 1
    )
    customer_orders["first_order_date"] = customer_orders.groupby("customer_id")[
        "order_date"
    ].transform("min")
    customer_orders["customer_type"] = np.where(
        customer_orders["customer_order_number"] == 1, "New", "Repeat"
    )

    df = df.merge(
        customer_orders,
        on=["customer_id", "order_id", "order_date"],
        how="left",
    )

    order_totals = (
        df.groupby("order_id", as_index=False)
        .agg(
            order_sales_total=("sales_amount", "sum"),
            order_profit_total=("profit_amount", "sum"),
            order_line_count=("row_id", "count"),
        )
        .round(2)
    )
    df = df.merge(order_totals, on="order_id", how="left")

    ordered_columns = [
        "row_id",
        "order_id",
        "order_date",
        "ship_date",
        "order_priority",
        "ship_mode",
        "customer_id",
        "customer_name",
        "customer_segment",
        "customer_type",
        "customer_order_number",
        "first_order_date",
        "geography_id",
        "province",
        "region",
        "product_id",
        "product_category",
        "product_sub_category",
        "product_name",
        "product_container",
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

    return df[ordered_columns].sort_values(
        ["order_date", "order_id", "row_id"]
    ).reset_index(drop=True)
