# hex-flyway-probability

A research project on probabilistic seabird flyway modelling over a hexagonal ocean grid.

## Project aim

This project extends the earlier seabird-flyways work by combining:
- least-cost path modelling on a hexagonal graph
- Markov-chain probability propagation across the same graph
- validation against arctic tern tracking data

The broader goal is to test whether migratory flyways are better represented as probabilistic movement corridors rather than single optimal paths.

## Repository structure

- `docs/` scientific framing and design documents
- `notes/` brainstorming and meeting notes
- `data/raw/` raw or copied source datasets
- `data/processed/` transformed project inputs
- `src/notebooks/` exploratory notebooks
- `src/scripts/` reusable code
- `results/figures/` generated figures
- `results/tables/` generated tables
- `refs/` relevant papers and references
- `notes/literature/` structured paper notes and cross-paper synthesis

## Current core documents

- `docs/PROJECT_OVERVIEW.md`
- `docs/CONCEPT_NOTE.md`
- `docs/TECHNICAL_DESIGN.md`
- `notes/NEXT_MEETING_QUESTIONS.md`

## Status

Project initialized. Scientific framing is in place. Next step is to prototype the hex grid and the transition framework.

## Working process

After each substantive project discussion:
- write dated meeting notes in `notes/meetings/YYYY-MM-DD.md`
- update the relevant core project documents in `docs/`
- overwrite `notes/NEXT_MEETING_QUESTIONS.md` with the current open agenda for the next session

For literature work:
- store PDFs once under `refs/`
- write structured summaries under `notes/literature/`
- build cumulative synthesis notes instead of re-reading papers from scratch each time
