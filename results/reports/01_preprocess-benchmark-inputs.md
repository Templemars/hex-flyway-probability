# Preprocess benchmark inputs

## Question
Create clean canonical Python-ready benchmark tables from the copied 2025 environmental CSVs.

## Input data
- `data/raw/benchmark_from_2025/springMeanSpeed.csv`
- `data/raw/benchmark_from_2025/chlSpring.csv`

## Method
- remove the extra export index column if present
- preserve recognizable field names
- write cleaned CSVs to `data/processed/benchmark_tables/`

## Key results
- produced `spring_wind_clean.csv`
- produced `spring_chla_clean.csv`
- both cleaned files contain 64,800 rows
- benchmark coverage is global, from -89.5 to 89.5 latitude and -180 to 179 longitude

## Summary table
See `results/tables/preprocess_benchmark_inputs_summary.csv`

## Interpretation
The benchmark environmental package is now available in a clean Python-ready form.
This step intentionally stops before any grid remapping or modelling.

## Next step
Inspect the cleaned tables and build the first benchmark square grid.
