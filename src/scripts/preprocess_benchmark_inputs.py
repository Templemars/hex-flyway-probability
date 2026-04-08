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

Current scope
-------------
1. Read the copied benchmark CSV files
2. Drop the extra export index column if present
3. Standardize column names
4. Write cleaned CSVs to data/processed/benchmark_tables/
5. Print a short summary so the user can inspect what happened

This script is intentionally narrow. It does not yet:
- build square or hex grids
- interpolate data
- compute movement costs
- run Dijkstra
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025"
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "benchmark_tables"


# Mapping from raw file names to cleaned output names.
INPUT_OUTPUT_MAP: Dict[str, str] = {
    "springMeanSpeed.csv": "spring_wind_clean.csv",
    "chlSpring.csv": "spring_chla_clean.csv",
}


def read_csv_rows(path: Path) -> List[List[str]]:
    """Read a CSV file into a list of rows.

    We keep the implementation deliberately simple here because the goal is
    transparency and easy debugging, not high-performance I/O.
    """
    with path.open("r", newline="") as handle:
        reader = csv.reader(handle)
        return list(reader)


def drop_export_index_column(rows: List[List[str]]) -> List[List[str]]:
    """Drop the leading export index column if it is present.

    In the copied benchmark files, the first header cell is empty, which signals
    that a dataframe index was written out during CSV export. We remove that
    column so the cleaned tables contain only meaningful scientific fields.
    """
    if not rows:
        return rows

    header = rows[0]
    if len(header) > 0 and header[0] == "":
        return [row[1:] for row in rows]

    return rows


def standardize_header(header: List[str]) -> List[str]:
    """Standardize header names very conservatively.

    We only strip whitespace here. We do not aggressively rename columns yet,
    because preserving recognizability from the original files is useful.
    """
    return [col.strip() for col in header]


def clean_rows(rows: List[List[str]]) -> List[List[str]]:
    """Apply the full cleaning pipeline to CSV rows."""
    rows = drop_export_index_column(rows)

    if not rows:
        return rows

    header = standardize_header(rows[0])
    data_rows = rows[1:]

    # Keep only rows with the same number of columns as the header.
    # This is a simple guard against malformed lines.
    clean_data_rows = [row for row in data_rows if len(row) == len(header)]

    return [header] + clean_data_rows


def write_csv_rows(path: Path, rows: List[List[str]]) -> None:
    """Write rows to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


def summarize_rows(rows: List[List[str]]) -> str:
    """Return a short human-readable summary of the cleaned table."""
    if not rows:
        return "empty table"

    header = rows[0]
    n_rows = max(0, len(rows) - 1)
    return f"rows={n_rows}, columns={len(header)}, fields={header}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Preprocessing benchmark environmental CSVs")
    print(f"Raw input directory: {RAW_DIR}")
    print(f"Output directory:    {OUT_DIR}")
    print()

    for input_name, output_name in INPUT_OUTPUT_MAP.items():
        input_path = RAW_DIR / input_name
        output_path = OUT_DIR / output_name

        rows = read_csv_rows(input_path)
        clean = clean_rows(rows)
        write_csv_rows(output_path, clean)

        print(f"Processed {input_name} -> {output_name}")
        print(f"  {summarize_rows(clean)}")
        print()

    print("Done.")


if __name__ == "__main__":
    main()
