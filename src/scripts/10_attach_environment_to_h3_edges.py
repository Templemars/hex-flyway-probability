#!/usr/bin/env python3
"""
Attach environmental values to the directed H3 edge table.

Purpose
-------
Create a transparent edge table that combines:
- directed H3 edge geometry
- source-cell environmental values
- target-cell environmental values where useful

Current scope
-------------
1. Read the H3 edge-geometry table
2. Read the H3 environmental table
3. Attach source and target environmental values to each edge
4. Write the enriched edge table

This step does not yet compute cost components.
It only prepares the data needed for that next step.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EDGE_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_geometry_res3.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_environment_res3.csv"


def main() -> None:
    edges = pd.read_csv(EDGE_PATH)
    env = pd.read_csv(ENV_PATH)

    source_env = env[["h3_cell", "u10", "v10", "speed", "chlor_a"]].rename(
        columns={
            "h3_cell": "source_h3",
            "u10": "source_u10",
            "v10": "source_v10",
            "speed": "source_speed",
            "chlor_a": "source_chlor_a",
        }
    )

    target_env = env[["h3_cell", "chlor_a"]].rename(
        columns={
            "h3_cell": "target_h3",
            "chlor_a": "target_chlor_a",
        }
    )

    out = edges.merge(source_env, on="source_h3", how="left")
    out = out.merge(target_env, on="target_h3", how="left")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    print("Attached environmental values to H3 edges")
    print(f"rows: {len(out)}")
    print(f"written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
