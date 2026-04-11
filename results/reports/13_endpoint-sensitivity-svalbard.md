# Endpoint sensitivity for Svalbard spring

## Question
How sensitive are the four current extreme-behavior routes to small changes in start and end H3 cells around the reference validation endpoints?

## Outputs
- route coordinates: `results/tables/13_svalbard_endpoint_sensitivity_coordinates.csv`
- tested endpoint pairs: `results/tables/13_svalbard_endpoint_sensitivity_endpoints.csv`
- route-to-reference similarity metrics: `results/tables/13_svalbard_endpoint_sensitivity_similarity.csv`
- overlay figure: `results/figures/13_svalbard_endpoint_sensitivity_routes.png`

## Quick-look figure

![Endpoint sensitivity over four background cost maps](../figures/13_svalbard_endpoint_sensitivity_routes.png)

## Run summary
- successful routes across all tested behavior-endpoint combinations: **324**
- random seed: **42**

## Behavior-level averages across non-reference routes
- `crosswind_only`: mean nearest-route distance ≈ **41.6 km**, mean P95 distance ≈ **273.3 km**, mean fraction within 1 H3 step ≈ **0.91**
- `distance_only`: mean nearest-route distance ≈ **74.1 km**, mean P95 distance ≈ **103.8 km**, mean fraction within 1 H3 step ≈ **0.74**
- `food_only`: mean nearest-route distance ≈ **12.1 km**, mean P95 distance ≈ **93.4 km**, mean fraction within 1 H3 step ≈ **0.96**
- `support_only`: mean nearest-route distance ≈ **11.9 km**, mean P95 distance ≈ **96.3 km**, mean fraction within 1 H3 step ≈ **0.98**

## Efficiency note
This reporting step reuses saved endpoint-sensitivity outputs and does not rerun the sensitivity routes.
