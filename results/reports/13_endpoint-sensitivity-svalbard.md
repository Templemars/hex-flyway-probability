# Endpoint sensitivity for Svalbard spring

## Question
How sensitive are the four current extreme-behavior routes to small changes in start and end H3 cells around the reference validation endpoints?

## Setup
- reference start cell: `83eea8fffffffff`
- reference end cell: `83076bfffffffff`
- tested behaviors: `support_only`, `crosswind_only`, `distance_only`, `food_only`
- tested start cells: reference cell plus randomly sampled cells from its H3 k=2 neighborhood
- tested end cells: reference cell plus randomly sampled cells from its H3 k=2 neighborhood
- random seed: `42`
- output route table kept intentionally compact, with coordinates only

## Outputs
- route coordinates: `results/tables/13_svalbard_endpoint_sensitivity_coordinates.csv`
- tested endpoint pairs: `results/tables/13_svalbard_endpoint_sensitivity_endpoints.csv`
- route-to-reference similarity metrics: `results/tables/13_svalbard_endpoint_sensitivity_similarity.csv`
- overlay figure: `results/figures/13_svalbard_endpoint_sensitivity_routes.png`

## Quick-look maps

### Support map
![Endpoint sensitivity over four background cost maps, support panel](../figures/13_svalbard_endpoint_sensitivity_routes.png)

### Crosswind map
![Endpoint sensitivity over four background cost maps, crosswind panel](../figures/13_svalbard_endpoint_sensitivity_routes.png)

### Distance map
![Endpoint sensitivity over four background cost maps, distance panel](../figures/13_svalbard_endpoint_sensitivity_routes.png)

### Food map
![Endpoint sensitivity over four background cost maps, food panel](../figures/13_svalbard_endpoint_sensitivity_routes.png)

## Map styling
- reference least-cost path shown in **red**
- alternative endpoint-sensitivity routes shown in **grey**
- backgrounds use the usual four component cost maps for direct comparison

## Run summary
- successful routes across all tested behavior-endpoint combinations: **324**

## Quantitative similarity to the reference route
The table `results/tables/13_svalbard_endpoint_sensitivity_similarity.csv` compares each grey sensitivity route to the red reference route for the same behavior.

Metrics included:
- symmetric mean nearest-route distance in km
- symmetric median nearest-route distance in km
- symmetric 95th-percentile nearest-route distance in km
- symmetric maximum nearest-route distance in km
- fraction of sensitivity-route points lying within roughly one H3 step of the reference route

Behavior-level averages across non-reference routes:
- `crosswind_only`: mean nearest-route distance ≈ **41.6 km**, mean P95 distance ≈ **273.3 km**, mean fraction within 1 H3 step ≈ **0.91**
- `distance_only`: mean nearest-route distance ≈ **74.1 km**, mean P95 distance ≈ **103.8 km**, mean fraction within 1 H3 step ≈ **0.74**
- `food_only`: mean nearest-route distance ≈ **12.1 km**, mean P95 distance ≈ **93.4 km**, mean fraction within 1 H3 step ≈ **0.96**
- `support_only`: mean nearest-route distance ≈ **11.9 km**, mean P95 distance ≈ **96.3 km**, mean fraction within 1 H3 step ≈ **0.98**

## Interpretation
This figure is useful because it asks a focused structural question before we broaden the behavior space: do small changes in endpoint placement materially alter the least-cost routes, or do the routes remain broadly organized by the cost field itself?

The encouraging part is that the sensitivity experiment can now be inspected both visually and quantitatively. The maps show corridor coherence directly, while the route-to-reference metrics summarize how tightly the grey bundles stay around the red reference path for each behavior.

The key thing to look for is whether each behavior preserves a recognizable corridor under moderate endpoint perturbation, not whether every grey line sits exactly on the red line. If the mean and P95 nearest-route distances stay modest and the within-one-step fraction remains high, that behavior looks more robust to endpoint choice. If those values deteriorate strongly, that behavior is more endpoint-sensitive and should be interpreted more cautiously.

So this step should be read as a diagnostic robustness check, not as a validation result by itself. Its job is to tell us whether the current prototype routes are structurally stable enough to justify the next stage of comparison and expansion.
