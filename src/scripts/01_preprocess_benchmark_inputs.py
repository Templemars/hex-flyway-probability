#!/usr/bin/env python3
"""
Preprocess benchmark CSV inputs copied from the 2025 seabird-flyways project.

Goal
----
Create clean, canonical Python-ready tables from the raw benchmark CSV files,
without yet performing any square-grid or hex-grid remapping.

Design principles
-----------------
- simplicity over cleverness
- explicit steps over compact tricks
- minimal dependencies
- easy to read, inspect, and modify
- reproducible file-in / file-out behavior
- pandas for CSV/tabular handling

Current scope
-------------
1. Read the copied benchmark CSV files with pandas
2. Drop the extra export index column if present
3. Standardize column names conservatively
4. Write cleaned CSVs to data/processed/benchmark_tables/
5. Print a short summary so the user can inspect what happened

This script is intentionally narrow. It does not yet:
- build square or hex grids
- interpolate data
- compute movement costs
- run Dijkstra
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025"
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "benchmark_tables"


INPUT_OUTPUT_MAP: Dict[str, str] = {
    "springMeanSpeed.csv": "spring_wind_clean.csv",
    "chlSpring.csv": "spring_chla_clean.csv",
}


def read_csv_table(path: Path) -> pd.DataFrame:
    """Read a raw benchmark CSV using pandas."""
    return pd.read_csv(path)


def drop_export_index_column(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the leading export index column if it is present.

    In the copied benchmark files, pandas reads the unnamed export index as an
    `Unnamed: 0` column. We remove it so the cleaned tables contain only
    meaningful scientific fields.
    """
    columns_to_drop = [col for col in df.columns if str(col).startswith("Unnamed:")]
    if columns_to_drop:
        return df.drop(columns=columns_to_drop)
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names very conservatively."""
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def clean_table(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the full cleaning pipeline to a benchmark table."""
    df = drop_export_index_column(df)
    df = standardize_columns(df)
    return df


def summarize_table(df: pd.DataFrame) -> str:
    """Return a short human-readable summary of a cleaned table."""
    return f"rows={len(df)}, columns={len(df.columns)}, fields={list(df.columns)}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Preprocessing benchmark environmental CSVs")
    print(f"Raw input directory: {RAW_DIR}")
    print(f"Output directory:    {OUT_DIR}")
    print()

    for input_name, output_name in INPUT_OUTPUT_MAP.items():
        input_path = RAW_DIR / input_name
        output_path = OUT_DIR / output_name

        df = read_csv_table(input_path)
        clean = clean_table(df)
        clean.to_csv(output_path, index=False)

        print(f"Processed {input_name} -> {output_name}")
        print(f"  {summarize_table(clean)}")
        print()

    print("Done.")


if __name__ == "__main__":
    main()
