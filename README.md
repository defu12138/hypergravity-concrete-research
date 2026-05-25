# Hypergravity Concrete Scout

This repository is a literature-scouting workspace for the "hypergravity concrete" topic.

The current GitHub-visible result is the **four-direction ScienceDirect-oriented refocus**. Earlier six-direction outputs are preserved as legacy/archive material and should not be mixed with the new four-direction review.

## Latest: Four-Direction Review

Use these files for the latest mentor-facing discussion:

- Configuration: `config/four_directions.yml`
- Search and processing script: `src/four_direction_sciencedirect.py`
- Final literature workbook: `data/processed/four_directions_literature.xlsx`
- Full screened table: `data/processed/four_directions_literature_all_screened.csv`
- Search logs: `logs/four_directions_sciencedirect_search_log.csv`
- Landscape report: `reports/four_directions_landscape.md`
- Comparison report: `reports/four_directions_comparison.md`
- Teacher meeting outline: `reports/teacher_meeting_outline.md`
- Legacy distinction note: `reports/legacy_six_direction_archive.md`

The four directions are:

1. Centrifuged / centrifugally cast / spun concrete
2. Geotechnical centrifuge modeling involving concrete structures
3. Gravity effects on cement hydration and microstructure
4. High-gravity carbonation / mineralization of cementitious or calcium-rich materials

The current workbook contains only ScienceDirect / Elsevier-sourced records. Supplemental sources such as Crossref, Semantic Scholar, or Google Scholar are not mixed into this workbook.

## Legacy: Six-Direction Review

The earlier six-direction scouting results remain in the repository for traceability:

- Legacy query set: `queries.yaml`
- Legacy processed tables: `data/processed/papers_master.csv`, `data/processed/works_master.csv`
- Legacy reports: `reports/final_research_map.md`, `reports/landscape_summary.md`, `reports/direction_score_report.md`, `reports/reading_list_by_direction.md`

Treat these as archive material. They are useful for background, but they are not the current four-direction ScienceDirect review.

## Data and API Rules

- Read `ELSEVIER_API_KEY` only from the environment.
- Do not write API keys to code, logs, reports, or commits.
- Do not scrape paid full text or bypass access controls.
- Store only lawful metadata, abstracts, DOI, stable links, and open/institutionally accessible metadata returned by official APIs.

## Running the Four-Direction Search

```powershell
python src/four_direction_sciencedirect.py --count 20
```

The script writes raw ScienceDirect/Elsevier metadata under `data/raw/sciencedirect_four_directions/`, processed outputs under `data/processed/`, reports under `reports/`, and API logs under `logs/`.

## Verification

```powershell
python -m pytest
```

The latest checked run passed all project tests.
