#!/usr/bin/env python3
"""
Write a short spring-only synthesis of the saved Svalbard and Netherlands
comparison outputs.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = PROJECT_ROOT / "results" / "tables"
REPORT_DIR = PROJECT_ROOT / "results" / "reports"

SUMMARY_PATH = TABLE_DIR / "18_svalbard_netherlands_comparison_summary.csv"
SPREAD_PATH = TABLE_DIR / "19_svalbard_netherlands_top20_route_spread.csv"
OUTPUT_PATH = REPORT_DIR / "20_spring-synthesis-svalbard-netherlands.md"


def main() -> None:
    summary = pd.read_csv(SUMMARY_PATH)
    spread = pd.read_csv(SPREAD_PATH)

    svalbard = summary.loc[summary["population"] == "svalbard_spring"].iloc[0]
    nl = summary.loc[summary["population"] == "netherlands_spring"].iloc[0]

    svalbard_spread = spread.loc[spread["population"] == "Svalbard spring"].copy()
    nl_spread = spread.loc[spread["population"] == "Netherlands spring"].copy()

    svalbard_mean_spread = float(svalbard_spread["lon_spread_p90_p10"].mean())
    nl_mean_spread = float(nl_spread["lon_spread_p90_p10"].mean())
    svalbard_max_band = svalbard_spread.sort_values("lon_spread_p90_p10", ascending=False).iloc[0]
    nl_max_band = nl_spread.sort_values("lon_spread_p90_p10", ascending=False).iloc[0]

    report = f'''# Spring-only synthesis: Svalbard versus Netherlands

## Scope
This is a provisional synthesis using the current **spring-only** comparisons for:
- Svalbard spring
- Netherlands spring

It is intentionally limited. It summarizes what appears shared across the two spring cases, what differs between them, and what should remain provisional until autumn cases are added.

## Shared pattern across both spring cases
The main shared result is that **wind remains central** in both populations. In both Svalbard spring and Netherlands spring, the best and top-ranked RMSE solutions place substantial weight on wind support. That suggests the H3 routing framework is not producing good flyway reconstructions from arbitrary coefficient mixtures. Instead, it repeatedly selects solutions in which wind assistance is an important part of the explanation.

## Population-specific difference
The two spring populations do **not** favor exactly the same coefficient regime.

- **Svalbard spring**
  - best RMSE: **{svalbard['best_rmse_km']:.1f} km**
  - best behavior weights: **({svalbard['a_wind']:.1f}, {svalbard['b_crosswind']:.1f}, {svalbard['c_distance']:.1f}, {svalbard['d_food']:.1f})**
  - interpretation: top solutions are more strongly **wind-dominant**

- **Netherlands spring**
  - best RMSE: **{nl['best_rmse_km']:.1f} km**
  - best behavior weights: **({nl['a_wind']:.1f}, {nl['b_crosswind']:.1f}, {nl['c_distance']:.1f}, {nl['d_food']:.1f})**
  - interpretation: top solutions place relatively more emphasis on **distance alongside wind**

This suggests that the same H3 modeling framework may be flexible enough to capture population-specific movement regimes, rather than collapsing both spring cases to one generic optimum.

## Route-family structure difference
The top-20 route families also differ structurally.

- mean top-20 longitude spread, **Svalbard spring**: **{svalbard_mean_spread:.2f} degrees**
- mean top-20 longitude spread, **Netherlands spring**: **{nl_mean_spread:.2f} degrees**

So under the current benchmark metric, the Svalbard spring top-20 family is broader than the Netherlands spring top-20 family. That means the Svalbard benchmark currently tolerates a wider family of good H3 routes, whereas the Netherlands benchmark appears to select a somewhat tighter corridor.

The widest latitude-band spread also differs:
- Svalbard spring widest band: **{svalbard_max_band['lat_band']}** with spread **{svalbard_max_band['lon_spread_p90_p10']:.2f} degrees**
- Netherlands spring widest band: **{nl_max_band['lat_band']}** with spread **{nl_max_band['lon_spread_p90_p10']:.2f} degrees**

That suggests the two populations are not only different in coefficient preference, but also different in where route-family flexibility is concentrated along latitude.

## What this means scientifically, for now
At this stage, the safest interpretation is:
- the H3 model appears able to reproduce meaningful aspects of both spring flyways
- wind importance is shared across populations
- but the details of the preferred movement regime are not identical between Svalbard and Netherlands spring

That is encouraging, because it means the framework is not trivially overfitting one single route logic. At the same time, it is still too early to generalize strongly across seasons.

## What remains provisional
This synthesis should remain explicitly provisional because:
- it uses only **spring** cases
- the endpoint rules are still prototype choices tied to the benchmark summaries
- the current validation metric is still based on 10-degree latitude-band longitude summaries
- autumn cases may reveal whether the current differences are population-specific, season-specific, or both

## Recommended next step
Extend the same workflow to the autumn simulations, then revisit this synthesis as a broader **population-by-season comparison** rather than treating the present spring-only pattern as final.
'''
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report)

    print("Wrote spring-only synthesis report")
    print(f"report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
