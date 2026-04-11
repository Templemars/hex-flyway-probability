# Run first H3 Dijkstra prototype

## Question
What happens when the first Svalbard spring H3 Dijkstra tests are run under four extreme single-factor behaviors, using the current prototype endpoint rule and the ERA5-supported routing mask?

## Outputs
- path table: `data/processed/routes/h3_dijkstra_svalbard_spring_paths.csv`
- route summary table: `results/tables/12_svalbard_dijkstra_summary.csv`
- weight table: `results/tables/12_svalbard_dijkstra_weight_sets.csv`
- endpoint table: `results/tables/12_svalbard_dijkstra_endpoints.csv`
- route figure: `results/figures/12_svalbard_dijkstra_routes.png`
- diagnostic overlay figure: `results/figures/12_component_maps_with_lcps.png`

## Quick-look figure

![First H3 Dijkstra prototype routes](../figures/12_svalbard_dijkstra_routes.png)

![Diagnostic component maps with corresponding least-cost paths](../figures/12_component_maps_with_lcps.png)

## Run status summary
- number of tested behaviors: **4**
- number of successful route runs: **4**
- number of failed route runs: **3**

## Efficiency note
This reporting step reuses saved step-12 route outputs and does not rerun Dijkstra.

Additional route summary:
- lowest total modeled path cost in this prototype batch: **food_only**
- corresponding total cost: **1308.804**
- corresponding total distance: **24460.9 km**
