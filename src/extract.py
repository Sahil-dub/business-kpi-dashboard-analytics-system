"""Raw data extraction utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import Settings


def extract_raw_sales_data(path: Path | None = None) -> pd.DataFrame:
    """Read the raw retail dataset into a DataFrame."""

    settings = Settings()
    source_path = path or settings.raw_dataset_path

    return pd.read_csv(
        source_path,
        encoding="latin1",
        low_memory=False,
    )
