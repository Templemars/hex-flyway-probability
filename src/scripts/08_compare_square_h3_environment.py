#!/usr/bin/env python3
"""
Compare the square-grid and H3-grid environmental fields.

Purpose
-------
Check whether the first H3 environmental assignment produces fields that are
close enough to the benchmark square-grid fields to proceed toward cost
construction.

Current scope
-------------
1. Read the cleaned square-grid environmental tables
2. Read the H3 environmental table
3. Summarize simple field statistics
4. Write a compact comparison table

Notes
-----
- wind comparisons use raw values
- chlorophyll should be inspected on a log scale in the reporting layer
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WIND_PATH = PROJECT_ROOT / "data" / "processed" / "benchmark_tables" / "spring_wind_clean.csv"
CHLA_PATH = PROJECT_ROOT / "data" / "processed" / "benchmark_tables" / "spring_chla_clean.csv"
H3_ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
OUTPUT_PATH = PROJECT_ROOT / "results" / "tables" / "08_compare_square_h3_environment_summary.csv"


def summarize_series(name: str, support: str, values: pd.Series) -> dict:
    clean = values.dropna()
    return {
        "variable": name,
        "support": support,
        "count": len(clean),
        "mean": clean.mean(),
        "median": clean.median(),
        "std": clean.std(),
        "min": clean.min(),
        "max": clean.max(),
    }


def main() -> None:
    wind = pd.read_csv(WIND_PATH)
    chla = pd.read_csv(CHLA_PATH)
    h3_env = pd.read_csv(H3_ENV_PATH)

    rows = []
    rows.append(summarize_series("speed", "square", wind["speed"]))
    rows.append(summarize_series("u10", "square", wind["u10"]))
    rows.append(summarize_series("v10", "square", wind["v10"]))
    rows.append(summarize_series("chlor_a", "square", chla["chlor_a"]))

    rows.append(summarize_series("speed", "h3", h3_env["speed"]))
    rows.append(summarize_series("u10", "h3", h3_env["u10"]))
    rows.append(summarize_series("v10", "h3", h3_env["v10"]))
    rows.append(summarize_series("chlor_a", "h3", h3_env["chlor_a"]))

    summary = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_PATH, index=False)

    print("Compared square-grid and H3 environmental fields")
    print(summary.to_string(index=False))
    print(f"written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
