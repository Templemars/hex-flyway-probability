# rWind method note

## What it is

`rWind` is an R package for direction-dependent wind/current connectivity analysis. It supports workflows in which environmental vector fields are turned into directional transition structures and then used for least-cost path analysis.

Core references now stored in the project:
- repository: `https://github.com/jabiologo/rWind`
- paper: `refs/methods/rwind-2019-ecography.pdf`

## Why it matters for this project

The package is directly relevant to the intellectual lineage of the 2025 seabird flyways paper. It reinforces a key conceptual point:

- movement cost is **direction-dependent**
- wind connectivity is **anisotropic**
- transitions from A to B are not generally equivalent to transitions from B to A

This strongly supports building the sequel as a **directed edge-cost graph** rather than as a simple static raster resistance surface.

## What to preserve from the rWind lineage

For the Python/H3 sequel, preserve these core ideas:

1. **Directional movement costs**
   - cost depends on movement direction relative to the local wind field

2. **Anisotropy**
   - favorable and unfavorable directions are not symmetric

3. **Transition-based modelling**
   - local movement should be represented on directed neighbor transitions

4. **Shortest-path logic as a movement model component**
   - least-cost path remains a valid core approach when the transition structure is well defined

## What to replace in the sequel

The sequel should not simply reproduce the old stack. Replace or modernize:

1. **R implementation**
   - replace with Python

2. **Square-grid / raster dependence**
   - replace with H3-based graph support

3. **Implicit inheritance from package defaults**
   - make formulas and assumptions explicit in our own code and docs

4. **Single-environment dependence without broader reporting structure**
   - wrap each implementation step with figures, summary tables, and milestone reports

## Scientific implication

The rWind lineage supports the decision that the heart of the new model should be an edge-based directional cost graph. The sequel differs mainly in:
- grid structure (H3 instead of square raster)
- software stack (Python instead of R)
- broader project framing (interannual variability, behavioural flexibility, exploratory Markov extension)

## Additional details from the 2019 Ecography software note

The paper makes several points that are directly relevant to the sequel design:
- standard connectivity tools based on friction layers are not naturally suited to wind because wind connectivity depends on both speed and direction
- wind connectivity is directional and target-dependent: it depends on wind at the source cell and the position of the target cell
- the default `rWind` movement-cost algorithm is explicitly anisotropic and computes cost from three ingredients:
  - wind speed at the starting cell
  - wind direction (azimuth) at the starting cell
  - the position of the target cell
- `rWind` can output either:
  - a sparse transition-cost matrix
  - or a conductance `TransitionLayer` for `gdistance`

Important algorithmic detail from the paper:
- the default cost formula is based on a **horizontal factor (HF)** and wind speed `S`
- active movement uses:
  - `Cost = HF / S`
- where `HF` depends on the horizontal relative moving angle (HRMA), i.e. the angle between wind azimuth and movement direction
- this again reinforces that the core object is a **directional source-to-target transition cost**, not a simple static resistance surface

## Follow-up

This note should later be expanded with:
- exact functions or concepts from rWind worth reproducing conceptually
- any formulas that need close comparison with the 2025 implementation
- explicit discussion of what the H3 version gains or loses relative to raster-based directional transitions
