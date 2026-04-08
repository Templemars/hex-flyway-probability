# Skyllas et al. 2025, seabird flyways

## Citation

Skyllas, N. et al. (2025). *Simulating and Analysing Seabird Flyways: An Approach Combining Least-Cost Path Modelling and Machine Learning*. Global Ecology and Biogeography.

## Why this paper matters here

This is the direct scientific predecessor of the current project. It defines the previous square-grid least-cost framework, the relevant environmental trade-offs, the tern flyway validation context, and the broad scientific motivation for the sequel project.

## Role in the new project

This paper serves as:
- the methodological baseline
- the biological benchmark for tern flyways
- the source of the decadal mean flyway framing
- the comparison point for the square-versus-hex redesign

## Immediate relevance

The new project should clearly state what it inherits from this paper and what it changes:
- square grid to hex grid
- stronger focus on climate-driven flyway stability and interannual variability
- exploratory Markov extension for climatically accessible movement space

## Specific method detail to retain

For flyway evaluation in the 2025 paper:
- the median starting location of each population was used as the simulation starting point
- the median longitudinal position of each population was calculated per 10° of latitude
- each simulated flyway was also summarized as median longitude per 10° latitude band
- RMSE was then calculated by comparing the simulated and observed longitude summaries across latitude bands
- the top 20 simulations with the lowest RMSE were selected for further analysis

This is important for the new project because it means any proposed secondary validation metric should not simply duplicate the same latitude-binned longitude comparison already embedded in the RMSE method.

## Follow-up

This note is currently a seed note. It should later be expanded with:
- exact methods reused
- exact limitations of the previous framework
- candidate text for manuscript framing
