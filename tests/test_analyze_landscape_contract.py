from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from analyze_landscape import analyze_works  # noqa: E402


def test_analyze_works_outputs_requested_report_figures_and_top_cited(tmp_path: Path) -> None:
    processed = tmp_path / "data" / "processed"
    reports = tmp_path / "reports"
    figures = tmp_path / "figures"
    processed.mkdir(parents=True)
    reports.mkdir()
    figures.mkdir()
    works_path = processed / "papers_master.csv"
    pd.DataFrame(
        [
            {
                "direction": "A",
                "direction_zh": "broken",
                "query": "q1",
                "title": "High gravity carbonation paper",
                "year": 2024,
                "authors": "Alice; Bob",
                "venue": "Journal A",
                "doi": "10/a",
                "url": "https://example.org/a",
                "abstract": "Abstract",
                "citation_count": 100,
                "source_database": "OpenAlex",
                "open_access_pdf": "unclear",
                "raw_id": "A1",
            },
            {
                "direction": "A",
                "direction_zh": "broken",
                "query": "q2",
                "title": "Another carbonation paper",
                "year": 2016,
                "authors": "Alice",
                "venue": "Journal A",
                "doi": "10/a2",
                "url": "https://example.org/a2",
                "abstract": "Abstract",
                "citation_count": 10,
                "source_database": "OpenAlex",
                "open_access_pdf": "unclear",
                "raw_id": "A2",
            },
            {
                "direction": "D",
                "direction_zh": "broken",
                "query": "q3",
                "title": "CO2 curing paper",
                "year": 2021,
                "authors": "Carol",
                "venue": "Journal D",
                "doi": "10/d",
                "url": "https://example.org/d",
                "abstract": "Abstract",
                "citation_count": 50,
                "source_database": "Semantic Scholar",
                "open_access_pdf": "unclear",
                "raw_id": "D1",
            },
            {
                "direction": "D",
                "direction_zh": "broken",
                "query": "q4",
                "title": "Older CO2 curing paper",
                "year": 2010,
                "authors": "Dan",
                "venue": "Journal D",
                "doi": "10/d2",
                "url": "https://example.org/d2",
                "abstract": "Abstract",
                "citation_count": 5,
                "source_database": "Crossref",
                "open_access_pdf": "unclear",
                "raw_id": "D2",
            },
        ]
    ).to_csv(works_path, index=False)
    queries_path = tmp_path / "queries.yaml"
    queries_path.write_text(
        yaml.safe_dump(
            {
                "directions": [
                    {"id": "A", "zh": "超重力碳化固废", "note_zh": "A relation"},
                    {"id": "D", "zh": "CO2养护与碳化混凝土", "note_zh": "D relation"},
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    outputs = analyze_works(works_path=works_path, processed_dir=processed, reports_dir=reports, figures_dir=figures, queries_path=queries_path)

    assert outputs["summary_report"].exists()
    assert outputs["direction_count_figure"].exists()
    assert outputs["year_trend_figure"].exists()
    assert outputs["top_venues_figure"].exists()
    assert outputs["top_cited"].exists()
    report = outputs["summary_report"].read_text(encoding="utf-8")
    assert "超重力碳化固废" in report
    assert "论文总数" in report
    assert "初步判断" in report
    top_cited = pd.read_csv(outputs["top_cited"])
    assert set(top_cited["direction"]) == {"A", "D"}
    assert top_cited.groupby("direction").size().max() <= 20
