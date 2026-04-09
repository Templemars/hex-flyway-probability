# Somveille, Manica and Rodrigues 2018, where the wild birds go

## Citation

Somveille, M., Manica, A., & Rodrigues, A.S.L. (2018). *Where the wild birds go: explaining the differences in migratory destinations across terrestrial bird species*. Ecography, 41, 1–12.

## Why this paper matters for the project

This paper is very relevant background and near-method context because it directly investigates why migratory birds end up in different breeding and non-breeding destinations. It focuses on trade-offs between distance, resources, temperature tracking, and habitat, which overlaps strongly with the conceptual questions behind our flyway work.

## Why it belongs in `refs/background/`

I classify it as background rather than direct methods because:
- it is focused on global macroecological explanation of migratory destinations across many species
- it does not provide the direct directional edge-cost construction we are implementing
- but it strongly informs the conceptual trade-offs we want to discuss and justify

## Main relevance from first read

The paper develops a null-model framework to test whether migratory destinations reflect trade-offs among:
- access to resources
- migration distance
- tracking temperature
- habitat conditions

From the abstract and introduction, the main conclusion is that migratory destinations are shaped by:
- better access to resources
- minimising travelled distance
- tracking temperature
- habitat appears less important than the others

## Why this is useful for our project

This paper matters because our current project is also built around explicit trade-offs. Even though our implementation is route-based and directional, the broader conceptual logic overlaps closely:
- climate and resources structure the movement system
- distance matters as a cost
- migration emerges from balancing gains and costs

This paper may help with:
- introduction framing for why distance/resource/climate trade-offs are biologically expected
- positioning our route model within a broader migration-destination literature
- justifying why multiple additive cost components are scientifically meaningful

## Relationship to our current work

This paper is conceptually close to the flyway project family, but it is not the direct technical template. It sits between background theory and modelling motivation.

In particular, it may help us discuss:
- why migration should reflect a trade-off rather than a single environmental driver
- how to motivate the inclusion of food, distance, and climate-related terms together
- how to discuss destination structure versus route structure

## Follow-up

This note should later be expanded with:
- the exact null-model logic used in the paper
- whether any of its terminology should influence our manuscript framing
- whether it should be cited alongside the 2021 migratory connectivity theory paper when explaining the broader ecological logic of the model
