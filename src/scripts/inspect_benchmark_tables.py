#!/usr/bin/env python3
"""
Inspect the cleaned benchmark tables.

Purpose
-------
Before building any grid logic, confirm that the cleaned benchmark tables:
- have the expected columns
- have sensible coordinate ranges
- have no obvious missing-value problems in key fields

This script stays intentionally simple and uses pandas only.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "processed" / "benchmark_tables"


def summarize_table(path: Path) -> None:
    df = pd.read_csv(path)

    print(f"\n===== {path.name} =====")
    print(f"rows: {len(df)}")
    print(f"columns: {list(df.columns)}")
    print()

    if "lon" in df.columns and "lat" in df.columns:
        print("coordinate ranges:")
        print(f"  lon: {df['lon'].min()} to {df['lon'].max()}")
        print(f"  lat: {df['lat'].min()} to {df['lat'].max()}")
        print()

    print("missing values by column:")
    print(df.isna().sum().to_string())
    print()

    print("first rows:")
    print(df.head(5).to_string(index=False))
    print()


def main() -> None:
    summarize_table(INPUT_DIR / "spring_wind_clean.csv")
    summarize_table(INPUT_DIR / "spring_chla_clean.csv")


if __name__ == "__main__":
    main()
