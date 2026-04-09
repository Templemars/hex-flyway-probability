# Technical design note

## 1. Overall framework

The project will be built around a graph representation of the migration domain.

Two graph discretizations will be compared:
- a square grid, to recreate the earlier framework as fairly as possible
- a hexagonal grid, as the proposed methodological improvement

The main validated framework is Dijkstra least-cost path modelling with a predefined destination. A secondary exploratory framework will use Markov transitions on the same hex grid but without a predefined destination.

## 2. Main analytical stages

### Stage A, square-versus-hex benchmark
- define a fair comparison between square and hex grids
- use decadal mean seasonal environmental fields
- simulate the same tern flyway on both grids
- compare both against the decadal mean observed flyway

### Stage B, interannual variability
- run the hex-grid Dijkstra framework on yearly seasonal mean environmental fields
- hold movement weights fixed
- quantify annual deviations from the decadal mean flyway

### Stage C, behavioural flexibility
- repeat annual simulations across a coarse set of movement weight combinations
- quantify how changing weight sets alters annual deviations from the decadal mean flyway
- interpret this as a model-based proxy for required behavioural flexibility

### Stage D, exploratory Markov analysis
- initialize movement from a Southern Ocean mask
- remove the destination constraint
- propagate movement probabilities across the hex grid
- map climatically accessible movement regions under different years and weight sets

## 3. Grid design

### 3.1 Square grid

Purpose:
- recreate the earlier modelling basis as a benchmark
- provide a fair baseline for comparison with the hex grid

Open design question:
- what defines a fair comparison? Possible criteria include similar node count, similar characteristic cell spacing, or similar cell area.

This fairness criterion must be decided explicitly before benchmarking.

### 3.2 Hex grid

Tasks:
- define the spatial domain
- choose hexagon resolution
- generate unique cell IDs
- calculate cell centroids
- define adjacency lists
- mask land if needed

Current selection logic:
- the benchmark CSVs are on a 1° global lat-lon grid
- H3 resolution should therefore be chosen by matching the global-mean area of a 1° cell as closely as possible
- a first comparison table has already been generated in `data/processed/grids/h3_resolution_comparison.csv`
- this comparison shows that the target lies between H3 resolutions 3 and 4
- benchmark choice for the first implementation: **H3 resolution 3**
- this must still be described explicitly as the closest standard H3 match in global-mean area terms, not as an exact area-equivalent replacement for the 1° grid

Outputs:
- hex cell geometry table
- adjacency table or graph object

### 3.3 Optional geometry diagnostics

Because one motivation for the hex grid is improved behaviour at high latitudes, we should consider simple geometric diagnostics in addition to predictive fit, for example:
- neighbor-distance consistency
- directional isotropy
- area consistency with latitude

These would support the square-versus-hex rationale independently of RMSE.

## 4. Environmental annotation

Environmental variables to project onto the grids:
- wind support
- crosswind
- chlorophyll-a or food proxy
- distance-related movement term

Input structure:
- decadal mean seasonal fields for the first benchmark
- yearly seasonal mean fields for interannual analyses

Immediate assumption:
- each season is treated as climatically stationary over the migration period, based on seasonal-average fields

## 4.1 Environmental transfer from the benchmark grid to H3

The benchmark environmental package is currently represented as a 1° global lat-lon support.
For the first H3 prototype, environmental values should be transferred to the H3 grid using a simple and explicit sampling rule.

Chosen first implementation:
- compute the centroid of each H3 cell
- sample the benchmark environmental field at that centroid
- use nearest-neighbor assignment as the first method

Reason for this choice:
- point-to-cell aggregation from the square support can leave some H3 cells empty if no benchmark centroids fall inside them
- centroid sampling gives each H3 cell a complete environmental record
- this is simpler and less ad hoc than aggregation-plus-gap-filling for the first prototype

Wind handling rule:
- treat `u10` and `v10` as the primary wind fields
- do not use raw wind direction as a directly averaged field in the first implementation
- recompute direction or derived wind quantities later if needed

This first centroid-sampling method is a prototype choice, not a claim of exact conservative remapping.
A more rigorous transfer method can be added later if needed.

## 5. Edge scoring and movement weights

Each move from cell i to neighboring cell j requires a score based on weighted movement drivers. A generic form is:

score(i,j) = a * wind_support + b * crosswind_term + c * distance_term + d * food_term

where the coefficients represent relative movement priorities rather than direct observed behaviours.

### 5.1 Dijkstra use
- convert the score into a movement cost
- compute least-cost paths from origin to destination

### 5.2 Markov use
- normalize neighbor scores into transition probabilities
- propagate occupancy probability from the starting mask over repeated steps

A softmax-like normalization remains a practical starting point:

P(i -> j) = exp(beta * score(i,j)) / sum over neighbors exp(beta * score(i,k))

This is provisional and should be treated as an implementation starting point, not as a finalized model statement.

## 6. Weight-set strategy

To keep the first phase practical and interpretable, the project should begin with a coarse weight-set table rather than a dense parameter search.

Suggested strategy:
- test a manageable number of combinations first
- include simple single-factor and two-factor combinations
- include several combinations inspired by the earlier paper
- refine only around promising combinations if needed

Crosswind may be introduced in the first coarse set or added in a second round. This remains an open design choice.

## 7. Dijkstra framework

Purpose:
- identify destination-constrained optimal flyways
- compare square and hex frameworks
- quantify interannual variability in optimal routes
- test sensitivity to movement weights

Outputs:
- path geometry
- cumulative path cost
- route summaries
- annual deviations from the decadal mean flyway

## 8. Markov framework

Purpose:
- estimate destination-free climatically accessible movement space
- explore how climate and weight sets shape broader migration envelopes
- test sensitivity to starting location by varying the Southern Ocean start mask if needed

Current assumptions:
- one step equals movement to a neighboring cell
- no explicit destination
- starting condition is a Southern Ocean non-breeding mask
- movement environment is seasonally fixed during a run

Open question:
- should remaining in the same cell be allowed as a transition?

## 9. Validation framework

Primary empirical material:
- decadal mean tern flyway from the earlier work

Reference objects to distinguish:
- **observed decadal mean flyway** as the biological benchmark
- **simulated decadal mean flyway** as the model baseline under average climate

Candidate metric structure:
- primary metric: RMSE relative to the decadal mean flyway
- secondary metric: at least one additional positional metric, such as median longitudinal deviation by latitude band
- optional endpoint or destination-region metric

For annual analyses, compare annual simulated flyways to:
- the observed decadal mean flyway
- the simulated decadal mean flyway

This separates biological mismatch from climate-driven model variability.

## 10. Implementation constraint

The sequel project should be implemented in **Python only**.

Implications:
- old R notebooks are reference material for methods and file provenance
- new simulation, preprocessing, and comparison code should be written in Python
- notation and method translation from the original R workflow must be made explicit to avoid silent inconsistencies

## 11. Immediate reusable inputs

From the previous project, the guide scripts already identify a likely first reusable input package for the spring prototype:
- `springMeanSpeed.csv`
- `chlSpring.csv`
- `gdf_SS_10.csv`
- `gdf_NS_10.csv`
- `coefflist.csv`
- `SScoordinates.csv`
- `NScoordinates.csv`

These files have now been copied into the new project so that the sequel can remain self-contained under:
- `data/raw/benchmark_from_2025/`

The first new prototype will probably only need a subset of these as active inputs, but they define the initial benchmark package.

### Input structure noted from the copied benchmark files

- `springMeanSpeed.csv` contains gridded rows with at least the fields:
  - `lat`
  - `lon`
  - `speed`
  - `u10`
  - `v10`
  - `dir`
- `chlSpring.csv` contains gridded rows with:
  - `lat`
  - `lon`
  - `chlor_a`
- both CSVs include an extra index column from export that should be dropped in Python preprocessing

This means the new Python implementation can reconstruct wind-derived movement quantities directly from the CSV package without first going back to NetCDF.

### Coefficient ordering convention for the Python sequel

Use the Python / paper ordering consistently in the new project:
- `a = wind`
- `b = crosswind`
- `c = distance`
- `d = food`

Do not reuse the old R notebook ordering internally in the new codebase. If old files or notebooks use a different ordering, translate them explicitly and document the translation.

## 12. Immediate implementation plan

### Phase 1
- recover and inspect the previous hexagon experiment
- choose the first tern population
- define the fairness criterion for square-versus-hex comparison

### Phase 2
- build grid-generation scripts for square and hex domains
- test neighborhood graphs and geometry diagnostics
- create the first Dijkstra benchmark on decadal mean fields

### Phase 3
- define the first coarse weight-set table
- benchmark square versus hex against the decadal mean flyway
- choose the best-performing or most interpretable weight sets

### Phase 4
- run yearly seasonal simulations on the hex grid
- quantify annual deviations and route stability
- examine how weight changes alter stability

### Phase 5
- implement the exploratory Markov framework on the same hex graph
- map accessible movement space under selected years and weight sets

## 13. Open technical questions

1. Which tern population should be used first?
2. What is the fairest square-versus-hex comparison criterion?
3. Which secondary metric should accompany RMSE?
4. Should crosswind enter the first-pass coarse weight set or be added later?
5. Should grid geometry be quantified explicitly in addition to predictive fit?
6. Should the Markov process allow staying in place?
7. How broad should the Southern Ocean starting mask be in the first exploratory analysis?

## 14. Immediate coding targets

1. `src/notebooks/01_hex_grid_prototype.ipynb`
2. `src/scripts/03_build_square_grid.py`
3. `src/scripts/build_hex_grid.py`
4. `src/scripts/build_dijkstra_inputs.py`
5. `src/notebooks/02_square_vs_hex_benchmark.ipynb`
