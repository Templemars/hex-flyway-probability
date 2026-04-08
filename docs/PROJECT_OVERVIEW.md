# Hex-grid flyway probability project

## Working idea

This project is the scientific sequel to the seabird-flyways work. The aim is to model migratory flyways not only as single least-cost paths, but also as probabilistic movement fields over an oceanic hexagonal grid.

The project will combine:
- graph-based least-cost path modelling using Dijkstra
- probabilistic movement using Markov chains
- environmental forcing from wind, food availability, and distance-related costs
- validation against arctic tern tracking data

## Scientific motivation

The previous project showed that observed flyways can be approximated by least-cost paths resulting from trade-offs between wind support, crosswind, distance, and food availability. However, observed migration is not necessarily well described by one deterministic optimal route. Real flyways may instead be structured as corridors of high movement probability.

A hexagonal grid offers a natural graph representation of marine movement space. On this graph, Dijkstra can identify optimal routes, while Markov transitions can estimate the probability that a simulated bird occupies different parts of the ocean after a number of movement steps.

## Core scientific question

Can migratory flyways be better represented as probabilistic movement landscapes rather than as single optimal paths, and does this improve our understanding of observed arctic tern flyways?

## Initial objectives

1. Build an oceanic hexagonal graph covering the relevant migration domain.
2. Map wind and food variables onto hexagons and graph edges.
3. Define edge costs and transition probabilities between neighboring cells.
4. Implement two complementary movement models:
   - least-cost path modelling
   - Markov-chain probability propagation
5. Validate both approaches against tern tracking data.
6. Quantify whether observed flyways are better matched by optimal paths, high-probability corridors, or both.

## Planned model hierarchy

- Model 1: Hex-grid Dijkstra using wind and distance
- Model 2: Hex-grid Markov chain using wind and distance
- Model 3: Hex-grid Markov chain using wind, distance, and food
- Optional Model 4: Markov model with directional persistence or destination attraction

## Immediate deliverables

- a concept note
- a technical design note
- a minimal hex-grid prototype
- a validation plan linked to the tern data

## Folder logic

- `docs/` for project-defining documents
- `notes/` for brainstorming and meeting-style scientific notes
- `data/raw/` for copied or linked source datasets
- `data/processed/` for gridded and transformed project inputs
- `src/notebooks/` for exploratory analysis
- `src/scripts/` for reusable code
- `results/` for figures and tables
- `refs/` for relevant papers, citations, and copied references
