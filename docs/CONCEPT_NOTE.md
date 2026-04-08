# Concept note

## Tentative title

Hexagonal-grid least-cost modelling of seabird flyways under climatic variability, with an exploratory extension to climatically accessible movement space

## Background

Large-scale migratory flyways emerge from interactions between animal movement behaviour and the physical environment. In pelagic migrants, wind conditions, travel distance, and food availability are likely central in shaping route selection. In the previous seabird-flyways project, these drivers were incorporated into a least-cost path framework and validated against arctic tern tracking data. That work demonstrated that combinations of wind support, crosswind, food availability, and distance can reproduce observed flyway patterns.

A key limitation of the earlier framework is geometric: it was implemented on a square grid, which is not ideal for movement analysis over high-latitude oceanic domains. Square cells produce anisotropy and become increasingly awkward toward the poles. A hexagonal grid should provide a more isotropic movement representation and may therefore improve simulation of flyways that extend across polar and subpolar regions.

A second limitation is climatic. If flyways are shaped by climate, then their stability should depend not only on average environmental conditions but also on interannual variability. If birds continue to use similar long-term flyways despite year-to-year climatic changes, then either the climate fields are stable enough or birds must be sufficiently flexible in how they weight different movement factors.

## Main idea

The main framework of this project is a destination-constrained least-cost path model implemented on a hexagonal graph. This framework will be validated against decadal mean tern flyways and directly compared against the earlier square-grid implementation.

The project then extends this validated framework in two directions:

1. **interannual variability**, by applying the same movement framework to yearly seasonal mean environmental fields
2. **behavioural flexibility**, by asking how much movement weighting must change across years to maintain similar long-term flyways

A secondary, exploratory extension will use a Markov movement process on the same hex grid, but without a predefined destination. This will allow us to map climatically accessible movement space and identify regions where migration is environmentally permissive even if no birds have yet been observed there.

## Main hypotheses

1. A hexagonal-grid least-cost framework will simulate tern flyways more accurately than the earlier square-grid framework.
2. Fixed movement priorities applied to yearly climate fields will produce measurable interannual variability in predicted flyways.
3. Maintaining a stable long-term flyway under yearly climatic variability will require some degree of flexibility in the relative weighting of wind, food, distance, and possibly crosswind.
4. Without a destination constraint, climate will still define structured regions of accessible movement, revealing a broader movement space than the realized flyway alone.

## Core scientific questions

### Question 1, geometry and validation
Does a hexagonal grid improve destination-constrained flyway simulation relative to the previous square-grid implementation?

### Question 2, interannual climatic variability
How much year-to-year variation in predicted flyways emerges when environmental fields vary but the movement weighting remains fixed?

### Question 3, behavioural flexibility
How much change in movement weighting is needed to keep predicted flyways close to the decadal mean flyway under varying yearly conditions?

### Question 4, climatically accessible movement space
What broader migration space becomes climatically accessible when birds are allowed to move without a predefined destination?

## Conceptual structure of the study

### Part I, main Dijkstra analysis
The main analysis will use Dijkstra least-cost paths on both square and hexagonal grids. It will be based initially on decadal mean seasonal environmental fields and compared against the decadal mean observed tern flyway. This is the core, validated, publication-driving part of the project.

### Part II, annual variability
The same hex-grid Dijkstra framework will then be run using seasonal averages from individual years. Annual flyways will be compared to the decadal mean flyway to estimate how strongly climate variability alone perturbs the route.

### Part III, behavioural flexibility
A coarse set of movement weight combinations will be tested across years. The purpose is not to infer exact behaviour, but to quantify how much change in the relative weighting of movement cues would be needed to maintain a similar flyway under variable climate. This should be framed carefully as a model-based proxy for behavioural flexibility.

### Part IV, exploratory Markov extension
The Markov component is not the main validated framework and should not be presented as a direct replacement for Dijkstra. Instead, it serves a different purpose: starting from a Southern Ocean mask, it will estimate climatically accessible movement regions under different environmental weightings. This extension is exploratory and biogeographical, intended to show the broader space of environmentally permissive movement.

## Validation and comparison logic

The first benchmark will be the decadal mean observed tern flyway from the earlier work. The first comparison will therefore be:
- square-grid Dijkstra versus observed decadal mean flyway
- hex-grid Dijkstra versus observed decadal mean flyway

For yearly analyses, two reference objects should be distinguished:
- the **observed decadal mean flyway**, which represents the biological benchmark
- the **simulated decadal mean flyway**, which represents the model baseline under average climate

This distinction allows us to separate biological mismatch from model-implied climatic variability.

## Candidate metrics

The primary metric will likely remain RMSE relative to the decadal mean flyway, to preserve continuity with the previous paper. However, RMSE alone is probably insufficient. At least one secondary positional metric should be included, for example:
- median longitudinal deviation by latitude band
- corridor or positional spread summary
- destination-region error

The exact choice remains open and should be decided before implementation.

## Why this could be publishable

The project has several linked contributions:
- a methodological comparison of square versus hexagonal movement grids
- an improved least-cost path framework for tern flyway simulation
- a climate-variability analysis of flyway stability
- a model-based estimate of the flexibility required to preserve similar flyways across variable years
- an exploratory map of broader climatically accessible movement space

Together, these elements support a biogeographical argument: climate does not only shape one realized flyway, but also structures the wider space of accessible migration pathways and constrains how stable realized flyways can remain through time.

## Immediate next scientific tasks

1. Choose the first tern population to analyze.
2. Define a fair square-versus-hex comparison.
3. Decide on the first metric set.
4. Build the first coarse weight-set table.
5. Reconstruct the hex-grid Dijkstra prototype before expanding the Markov framework.
