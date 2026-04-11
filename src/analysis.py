"""KPI generation and Power BI-ready exports."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / "outputs" / ".matplotlib"))

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from src.config import Settings

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

matplotlib.use("Agg")


def _metric_frame(rows: list[tuple[str, float | int | str]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["metric", "value"])


def generate_kpi_summary(clean_df: pd.DataFrame) -> pd.DataFrame:
    order_level = clean_df.groupby("order_id", as_index=False).agg(
        order_revenue=("sales_amount", "sum"),
        order_profit=("profit_amount", "sum"),
    )
    total_customers = int(clean_df["customer_id"].nunique())
    repeat_customers = int(
        clean_df.loc[clean_df["customer_type"] == "Repeat", "customer_id"].nunique()
    )
    one_time_customers = total_customers - repeat_customers

    return _metric_frame(
        [
            ("total_revenue", round(clean_df["sales_amount"].sum(), 2)),
            ("total_profit", round(clean_df["profit_amount"].sum(), 2)),
            (
                "profit_margin_pct",
                round(
                    (clean_df["profit_amount"].sum() / clean_df["sales_amount"].sum()) * 100,
                    2,
                ),
            ),
            ("total_orders", int(clean_df["order_id"].nunique())),
            ("total_customers", total_customers),
            ("average_order_value", round(order_level["order_revenue"].mean(), 2)),
            ("average_order_profit", round(order_level["order_profit"].mean(), 2)),
            ("repeat_customers", repeat_customers),
            ("one_time_customers", one_time_customers),
            (
                "repeat_customer_rate_pct",
                round((repeat_customers / total_customers) * 100, 2),
            ),
        ]
    )


def monthly_revenue_trend(clean_df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        clean_df.groupby("order_month_start", as_index=False)
        .agg(
            revenue=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .sort_values("order_month_start")
    )
    monthly["average_order_value"] = monthly["revenue"] / monthly["orders"]
    monthly["mom_revenue_growth_pct"] = monthly["revenue"].pct_change() * 100
    return monthly.round(2)


def top_products(clean_df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    return (
        clean_df.groupby(["product_id", "product_name", "product_category"], as_index=False)
        .agg(
            revenue=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            quantity=("order_quantity", "sum"),
            orders=("order_id", "nunique"),
        )
        .assign(profit_margin_pct=lambda df: (df["profit"] / df["revenue"]) * 100)
        .sort_values(["revenue", "profit"], ascending=False)
        .head(limit)
        .round(2)
    )


def category_performance(clean_df: pd.DataFrame) -> pd.DataFrame:
    return (
        clean_df.groupby(["product_category", "product_sub_category"], as_index=False)
        .agg(
            revenue=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            quantity=("order_quantity", "sum"),
            orders=("order_id", "nunique"),
        )
        .assign(profit_margin_pct=lambda df: (df["profit"] / df["revenue"]) * 100)
        .sort_values(["revenue", "profit"], ascending=False)
        .round(2)
    )


def regional_performance(clean_df: pd.DataFrame) -> pd.DataFrame:
    return (
        clean_df.groupby(["region", "province"], as_index=False)
        .agg(
            revenue=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .assign(profit_margin_pct=lambda df: (df["profit"] / df["revenue"]) * 100)
        .sort_values(["revenue", "profit"], ascending=False)
        .round(2)
    )


def customer_summary(clean_df: pd.DataFrame) -> pd.DataFrame:
    return (
        clean_df.groupby(["customer_id", "customer_name", "customer_segment"], as_index=False)
        .agg(
            first_order_date=("first_order_date", "min"),
            latest_order_date=("order_date", "max"),
            orders=("order_id", "nunique"),
            revenue=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
        )
        .assign(
            customer_status=lambda df: df["orders"].map(
                lambda value: "Repeat" if value > 1 else "New"
            ),
            avg_order_value=lambda df: df["revenue"] / df["orders"],
        )
        .sort_values(["revenue", "profit"], ascending=False)
        .round(2)
    )


def customer_segment_summary(clean_df: pd.DataFrame) -> pd.DataFrame:
    return (
        clean_df.groupby(["customer_segment", "customer_type"], as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            revenue=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            orders=("order_id", "nunique"),
        )
        .assign(avg_order_value=lambda df: df["revenue"] / df["orders"])
        .sort_values(["revenue"], ascending=False)
        .round(2)
    )


def low_performing_products(clean_df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    product_summary = (
        clean_df.groupby(["product_id", "product_name", "product_category"], as_index=False)
        .agg(
            revenue=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            quantity=("order_quantity", "sum"),
            orders=("order_id", "nunique"),
        )
        .assign(profit_margin_pct=lambda df: (df["profit"] / df["revenue"]) * 100)
    )

    return (
        product_summary.loc[product_summary["orders"] >= 3]
        .sort_values(["profit", "profit_margin_pct", "revenue"], ascending=[True, True, False])
        .head(limit)
        .round(2)
    )


def export_analysis_outputs(clean_df: pd.DataFrame, settings: Settings) -> dict[str, pd.DataFrame]:
    outputs = {
        "kpi_summary": generate_kpi_summary(clean_df),
        "monthly_revenue": monthly_revenue_trend(clean_df),
        "top_products": top_products(clean_df),
        "top_categories": category_performance(clean_df),
        "top_regions": regional_performance(clean_df),
        "customer_segments": customer_segment_summary(clean_df),
        "customer_summary": customer_summary(clean_df),
        "low_performing_products": low_performing_products(clean_df),
    }

    outputs["kpi_summary"].to_csv(settings.kpi_summary_path, index=False)
    outputs["monthly_revenue"].to_csv(settings.monthly_revenue_path, index=False)
    outputs["top_products"].to_csv(settings.top_products_path, index=False)
    outputs["top_categories"].to_csv(settings.top_categories_path, index=False)
    outputs["top_regions"].to_csv(settings.top_regions_path, index=False)
    outputs["customer_segments"].to_csv(settings.customer_segments_path, index=False)
    outputs["customer_summary"].to_csv(settings.customer_summary_path, index=False)
    outputs["low_performing_products"].to_csv(settings.low_performing_products_path, index=False)

    generate_charts(outputs, settings.charts_dir)
    return outputs


def generate_charts(outputs: dict[str, pd.DataFrame], charts_dir: Path) -> None:
    charts_dir.mkdir(parents=True, exist_ok=True)

    monthly = outputs["monthly_revenue"]
    plt.figure(figsize=(10, 5))
    plt.plot(monthly["order_month_start"], monthly["revenue"], linewidth=2)
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(charts_dir / "monthly_revenue_trend.png", dpi=200)
    plt.close()

    categories = outputs["top_categories"].groupby("product_category", as_index=False).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
    )
    plt.figure(figsize=(8, 5))
    plt.bar(categories["product_category"], categories["profit"])
    plt.title("Profit by Product Category")
    plt.xlabel("Category")
    plt.ylabel("Profit")
    plt.tight_layout()
    plt.savefig(charts_dir / "category_profitability.png", dpi=200)
    plt.close()


def run_sql_exports(engine: "Engine", settings: Settings) -> dict[str, pd.DataFrame]:
    """Execute named SQL queries and return the results."""

    from sqlalchemy import text

    sql_text = (settings.sql_dir / "kpi_queries.sql").read_text(encoding="utf-8")
    chunks = [chunk.strip() for chunk in sql_text.split("-- name:") if chunk.strip()]
    outputs: dict[str, pd.DataFrame] = {}

    with engine.begin() as connection:
        for chunk in chunks:
            name_line, query = chunk.split("\n", 1)
            output_name = name_line.strip()
            rendered_query = query.replace("{{schema}}", settings.postgres_schema)
            outputs[output_name] = pd.read_sql_query(text(rendered_query), connection)

    return outputs
