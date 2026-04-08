# Technical design note

## 1. Overall framework

We will represent the migration domain as a hexagonal graph:
- nodes = hexagonal ocean cells
- edges = adjacency between neighboring hexagons

Each edge will carry environmental and geometric attributes that determine either:
- a movement cost for least-cost path analysis
- a movement probability for Markov propagation

## 2. Main components

### 2.1 Hexagonal grid

Tasks:
- define the spatial domain
- choose hexagon resolution
- generate unique cell IDs
- calculate cell centroids
- define adjacency lists
- mask land if needed

Outputs:
- hex cell geometry table
- adjacency table or graph object

### 2.2 Environmental annotation

Environmental variables to project onto the grid:
- wind support
- crosswind
- chlorophyll-a or food proxy
- optional derived distance/progress metrics

Questions to resolve:
- are variables stored per cell, per season, per month, or per time step?
- are edge values computed from source cell, target cell, or edge direction?

### 2.3 Edge scoring

Each move from cell i to neighboring cell j requires a score. A generic form is:

score(i,j) = f(wind support, crosswind, food, distance)

Then:
- Dijkstra cost can be defined as a monotonic inverse of desirability
- Markov transition probability can be defined via normalization across neighbors

Possible probability form:

P(i -> j) = exp(beta * score(i,j)) / sum over neighbors exp(beta * score(i,k))

This should be treated as an initial candidate, not a fixed final form.

### 2.4 Dijkstra mode

Purpose:
- identify one or several optimal routes between origin and destination regions
- compare with the previous least-cost framework

Outputs:
- least-cost path geometry
- cumulative path cost
- route summaries

### 2.5 Markov mode

Purpose:
- propagate occupancy probabilities over the graph across steps
- estimate route corridors and spatial uncertainty

Outputs:
- occupancy distributions after each step
- cumulative visitation probability
- most likely corridors

## 3. Validation framework

Primary empirical material:
- arctic tern tracking data from the previous project

Candidate validation products:
- occupancy overlap maps
- median track position versus simulated probability ridge
- corridor width comparison
- destination-region capture
- path similarity relative to least-cost model

## 4. Implementation plan

### Stage 1
- recover and inspect the previous hexagon experiment
- build a clean prototype notebook or script for hex grid generation
- test neighborhood graph correctness

### Stage 2
- define a toy transition score on a synthetic grid
- run Dijkstra and Markov propagation on the same toy graph
- visualize route versus occupancy field

### Stage 3
- import real tern-related environmental inputs
- aggregate them to the hex grid
- define seasonal or monthly transition layers

### Stage 4
- run validation against tern flyways
- compare model hierarchy

## 5. Open technical questions

1. What should be the hex size?
2. What should one step represent?
3. Should movement allow only immediate neighbors, or also second-ring moves?
4. Should destination attraction be explicit?
5. How should seasonality enter the transition matrix?
6. Is one transition matrix enough, or do we need time-varying matrices?
7. Should path memory be absent, weak, or explicit?

## 6. Immediate coding targets

1. `src/notebooks/01_hex_grid_prototype.ipynb`
2. `src/scripts/build_hex_grid.py`
3. `src/scripts/build_transition_matrix.py`
4. `src/notebooks/02_toy_dijkstra_vs_markov.ipynb`
