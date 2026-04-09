# Revell and Somveille 2017, physics-inspired model of migratory routes

## Citation

Revell, A., & Somveille, M. (2017). *A physics-inspired mechanistic model of migratory movement patterns in birds*. Scientific Reports.

## Why this paper matters for the project

This paper looks highly relevant to the hex-grid sequel because it develops a mechanistic movement model for bird migration that is explicitly inspired by movement physics and route optimization. It is methodologically relevant because our current project is also trying to build a transparent movement algorithm rather than rely on black-box software.

## Main relevance from first read

From the opening sections, the paper appears to:
- frame migratory movement as a mechanistic process rather than only a pattern-fitting exercise
- emphasize explicit route-generation logic
- connect movement structure with physical/environmental constraints
- provide a useful comparison point for how much biological realism and mechanistic explicitness we want in our own model

## Why it is in `refs/methods/`

This paper is best treated as a methods paper rather than a core lineage paper.
It is not part of the direct flyway-project ancestry in the way the 2023 and 2025 Skyllas papers are, but it may help us think about:
- mechanistic route generation
- physical interpretation of movement costs
- how to frame a transparent movement model in the manuscript

## Likely value for our sequel

This paper may be especially useful when we discuss:
- whether the H3 model should be described as a mechanistic route model
- how to justify the directional edge-cost structure biologically
- how much model complexity is scientifically defensible
- how to connect a graph-based migration model to broader movement theory

## Follow-up

This is an initial note only. Later it should be expanded with:
- the exact movement assumptions in the paper
- what is mechanistically similar to our approach
- what is different from our wind-food-distance framework
- whether there are framing or validation ideas we should borrow
