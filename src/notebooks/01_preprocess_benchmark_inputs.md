# 01 preprocess benchmark inputs

## Purpose

This is the first implementation step of the new project.

The goal is deliberately modest:
- read the copied benchmark CSV files from the 2025 project
- remove export artifacts
- produce clean canonical tables for Python work

We do **not** yet:
- build the square grid
- build the hex grid
- interpolate data
- calculate movement costs
- run Dijkstra

## Input files

From `data/raw/benchmark_from_2025/`:
- `springMeanSpeed.csv`
- `chlSpring.csv`

## Output files

Written to `data/processed/benchmark_tables/`:
- `spring_wind_clean.csv`
- `spring_chla_clean.csv`

## Reasoning

The point of this first step is to keep preprocessing separate from modelling.
That makes the later code easier to debug and easier to explain.

The cleaned benchmark tables will act as the canonical environmental input layer for the first prototype.

## Current findings

- `springMeanSpeed.csv` contains:
  - `lat`, `lon`, `speed`, `u10`, `v10`, `dir`
- `chlSpring.csv` contains:
  - `lat`, `lon`, `chlor_a`
- both raw files included an extra export index column, which has now been removed
- both cleaned tables contain 64,800 rows

## Script

See:
- `src/scripts/preprocess_benchmark_inputs.py`
