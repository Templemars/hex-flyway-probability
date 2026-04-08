# Hex-grid flyway probability project

## Working idea

This project is the scientific sequel to the seabird-flyways work. The main goal is to rebuild the earlier least-cost path framework on a hexagonal ocean grid and test whether this improves flyway simulation relative to the earlier square-grid approach, especially at high latitudes.

The project has two linked parts:
- a **main validated framework** based on Dijkstra least-cost paths to explain observed tern flyways
- a **secondary exploratory framework** based on Markov transitions to map climatically accessible movement space without a predefined destination

## Scientific motivation

The previous project showed that observed tern flyways can be approximated by least-cost paths resulting from trade-offs between wind support, crosswind, distance, and food availability. However, that framework was built on a square grid, which is a poor geometric representation at high latitudes and may distort movement structure near the poles.

A hexagonal grid should provide a more isotropic movement graph and a better spatial basis for migration modelling over polar and oceanic regions. Beyond the geometric improvement, this project asks how stable predicted flyways are under interannual climatic variability and how much flexibility in movement weighting would be required to maintain similar long-term flyways.

## Core scientific questions

1. Does a hexagonal grid improve flyway simulation relative to the previous square-grid implementation?
2. How much interannual flyway variability emerges when movement priorities are held fixed but yearly climate fields vary?
3. How much flexibility in movement weighting is required to maintain a stable long-term flyway under variable yearly climate?
4. What broader climatically accessible movement space emerges when destination constraints are removed?

## Main project structure

### Part I, main validated analysis
- compare square-grid and hex-grid Dijkstra simulations
- use decadal mean seasonal environmental fields
- validate against the decadal mean observed tern flyway
- identify promising weight combinations for wind, crosswind, food, and distance

### Part II, interannual variability and behavioural flexibility
- use yearly seasonal mean environmental fields
- simulate annual flyways for fixed weight sets
- quantify deviation from the decadal mean flyway
- test how changing weight sets alters flyway stability across years

### Part III, exploratory Markov extension
- use the same hex grid without a destination constraint
- initialize movement from a Southern Ocean starting mask
- map climatically accessible movement space under different weight sets and years
- treat this as exploratory and hypothesis-generating rather than as the main validation core

## Immediate priorities

1. Choose the first tern population / flyway to analyze.
2. Define a fair square-versus-hex comparison.
3. Specify the first metric set, likely RMSE plus at least one secondary positional metric.
4. Build the first coarse weight-set table.
5. Reconstruct the hex-grid prototype and the Dijkstra pipeline before expanding the Markov work.

## Folder logic

- `docs/` project-defining scientific documents
- `notes/` brainstorming and meeting notes
- `data/raw/` copied or linked source datasets
- `data/processed/` gridded and transformed inputs
- `src/notebooks/` exploratory analysis
- `src/scripts/` reusable code
- `results/` figures and tables
- `refs/` relevant papers and references
