"""Pipeline entrypoint for the Business KPI Dashboard project."""

from __future__ import annotations

import logging

from src.analysis import export_analysis_outputs
from src.config import Settings, ensure_directories
from src.extract import extract_raw_sales_data
from src.load import load_to_postgres
from src.transform import clean_sales_data


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def run_pipeline() -> None:
    settings = Settings()
    ensure_directories(settings)

    LOGGER.info("Extracting raw sales data from %s", settings.raw_dataset_path)
    raw_df = extract_raw_sales_data(settings.raw_dataset_path)

    LOGGER.info("Transforming %s raw records", len(raw_df))
    clean_df = clean_sales_data(raw_df)

    LOGGER.info("Writing cleaned dataset to %s", settings.processed_dataset_path)
    clean_df.to_csv(settings.processed_dataset_path, index=False)
    clean_df.to_csv(settings.cleaned_output_path, index=False)

    LOGGER.info("Generating KPI outputs and chart assets")
    export_analysis_outputs(clean_df, settings)

    if settings.is_database_configured:
        LOGGER.info("Database credentials found; loading star schema into PostgreSQL")
        load_to_postgres(clean_df, settings)
    else:
        LOGGER.warning(
            "Skipping PostgreSQL load because POSTGRES_PASSWORD is not configured. "
            "Set variables from .env.example to enable database loading."
        )

    LOGGER.info("Pipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()
