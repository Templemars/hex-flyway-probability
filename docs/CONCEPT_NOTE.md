# Concept note

## Tentative title

From optimal flyways to probabilistic migration corridors: modelling seabird migration on a hexagonal ocean grid using least-cost paths and Markov chains

## Background

Large-scale migratory flyways emerge from interactions between animal movement behaviour and the physical environment. In pelagic migrants, wind conditions, travel distance, and resource availability are likely central in shaping route selection. In the previous seabird-flyways project, these drivers were incorporated into a least-cost path framework and validated against arctic tern tracking data. That work demonstrated that combinations of wind support, crosswind, food availability, and distance can reproduce observed flyway patterns.

A remaining limitation of least-cost path approaches is that they typically emphasize a single optimal route or a small set of best routes. Real migrations, however, may be better represented as spatial probability fields or corridors, where some ocean regions are more likely to be traversed than others. This is particularly relevant when multiple environmentally favorable alternatives exist, when tracking data show corridor-like spread, or when route choice depends on cumulative local movement decisions rather than on a globally optimal path.

## Main idea

We propose a graph-based framework on a hexagonal grid in which migratory movement is represented in two complementary ways:

1. as a least-cost path problem, identifying optimal routes through the graph
2. as a Markov movement process, estimating the probability distribution of bird locations after successive movement steps

In both cases, movement between neighboring hexagons will depend on environmental and geometric quantities such as wind, food availability, and distance. This makes it possible to directly compare deterministic optimal-route predictions with probabilistic migration-corridor predictions.

## Main hypothesis

Observed tern flyways are better described as high-probability movement corridors shaped by local environmental decisions than as a single globally optimal path.

## Supporting hypotheses

1. A hex-grid least-cost model should recover broad features of the previously inferred flyways.
2. A Markov-chain model should capture corridor width and alternative routes better than a pure least-cost model.
3. Including food availability in addition to wind and distance should improve agreement with observed tern flyway distributions.
4. The comparison between least-cost and Markov predictions can reveal whether different flyways are narrow optimal routes or broader probabilistic corridors.

## Core modelling ingredients

### State space

The ocean is discretized into hexagonal grid cells. Each cell is a node in a graph, and neighboring hexagons define possible movement transitions.

### Transition structure

At each step, a bird can move from one hexagon to one of its neighboring cells. The relative attractiveness of each move will be determined from a transition score based on:
- wind support
- crosswind or wind misalignment
- distance or geometric displacement toward migration progress
- food availability

These scores can be used in two ways:
- converted into edge costs for Dijkstra
- normalized into edge probabilities for a Markov process

### Outputs

The framework should produce:
- least-cost routes
- stepwise occupancy probability maps
- high-probability corridors
- summary statistics comparable to the observed flyway structure

## Validation idea

The first validation target should be the same tern flyways used in the earlier project. This ensures continuity and allows a clean comparison with the prior least-cost path framework.

Potential validation targets include:
- overlap between observed tracks and predicted high-probability areas
- similarity between observed and simulated median flyway positions
- spread or corridor width of observed versus simulated movement
- arrival-region accuracy
- comparison of least-cost versus Markov prediction skill

## Why this could be publishable

The publishable contribution is not only a new grid geometry. The real contribution is conceptual and methodological:
- replacing or complementing single-route optimality with probabilistic movement landscapes
- showing how local transition rules can generate emergent flyway corridors
- comparing deterministic and probabilistic graph-based migration models on the same empirical system

If successful, this could provide a more realistic framework for understanding flyway flexibility, uncertainty, and environmental sensitivity.

## Immediate next scientific tasks

1. Define what one Markov step means biologically and computationally.
2. Decide whether the Markov model is memoryless or includes directional persistence.
3. Define the baseline transition score mathematically.
4. Specify the headline validation metric.
5. Build a minimal hex-grid prototype before integrating the full environmental datasets.
