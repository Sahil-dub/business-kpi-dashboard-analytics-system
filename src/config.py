"""Project configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Central configuration for paths and database access."""

    root_dir: Path = Path(__file__).resolve().parents[1]
    data_dir: Path = root_dir / "data"
    raw_dir: Path = data_dir / "raw"
    processed_dir: Path = data_dir / "processed"
    output_dir: Path = root_dir / "outputs"
    charts_dir: Path = output_dir / "charts"
    sql_dir: Path = root_dir / "sql"

    raw_dataset_path: Path = raw_dir / "superstore_sales.csv"
    processed_dataset_path: Path = processed_dir / "cleaned_sales_dataset.csv"
    cleaned_output_path: Path = output_dir / "cleaned_dataset.csv"
    kpi_summary_path: Path = output_dir / "kpi_summary.csv"
    monthly_revenue_path: Path = output_dir / "monthly_revenue.csv"
    top_products_path: Path = output_dir / "top_products.csv"
    top_categories_path: Path = output_dir / "top_categories.csv"
    top_regions_path: Path = output_dir / "top_regions.csv"
    customer_segments_path: Path = output_dir / "customer_segments.csv"
    low_performing_products_path: Path = output_dir / "low_performing_products.csv"
    customer_summary_path: Path = output_dir / "customer_summary.csv"

    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "business_kpi")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_schema: str = os.getenv("POSTGRES_SCHEMA", "analytics")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_database_configured(self) -> bool:
        return bool(self.postgres_password)


def ensure_directories(settings: Settings) -> None:
    """Create expected project directories if they do not already exist."""

    for path in (
        settings.raw_dir,
        settings.processed_dir,
        settings.output_dir,
        settings.charts_dir,
        settings.sql_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)
