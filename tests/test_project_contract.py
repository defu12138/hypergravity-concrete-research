from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from common import normalize_doi, title_key  # noqa: E402
from merge_and_clean import clean_records, sample_records  # noqa: E402
from analyze_landscape import analyze_works  # noqa: E402
from select_reading_list import select_reading_list  # noqa: E402
from score_directions import score_directions  # noqa: E402


def test_queries_define_six_directions() -> None:
    data = yaml.safe_load((PROJECT_ROOT / "queries.yaml").read_text(encoding="utf-8"))
    ids = [direction["id"] for direction in data["directions"]]
    assert ids == ["A", "B", "C", "D", "E", "F"]
    assert all(direction["queries"] for direction in data["directions"])
    assert "rotating packed bed" in " ".join(
        query for direction in data["directions"] for query in direction["queries"]
    )


def test_common_normalizers_are_stable() -> None:
    assert normalize_doi("https://doi.org/10.1000/ABC") == "10.1000/abc"
    assert normalize_doi("") == "unclear"
    assert title_key("  CO2-curing Concrete! ") == "co2 curing concrete"


def test_clean_records_dedupes_and_keeps_unclear() -> None:
    cleaned, stats = clean_records(sample_records())
    works = pd.DataFrame(cleaned)

    assert len(works) == 3
    assert "unclear" in set(works["doi"])
    assert stats["missing_doi_count"] == 1
    assert works["duplicate_count"].max() == 2


def test_analysis_reading_list_and_scores_write_outputs(tmp_path: Path) -> None:
    processed = tmp_path / "data" / "processed"
    reports = tmp_path / "reports"
    figures = tmp_path / "figures"
    processed.mkdir(parents=True)
    reports.mkdir()
    figures.mkdir()

    works = pd.DataFrame(clean_records(sample_records())[0])
    works_path = processed / "works_master.csv"
    works.to_csv(works_path, index=False)

    analysis_outputs = analyze_works(works_path, processed, reports, figures)
    reading_outputs = select_reading_list(works_path, processed, reports, per_direction=2)
    score_outputs = score_directions(processed, reports)

    assert analysis_outputs["direction_summary"].exists()
    assert analysis_outputs["report"].exists()
    assert analysis_outputs["trend_figure"].exists()
    assert reading_outputs["csv"].exists()
    assert reading_outputs["report"].exists()
    assert score_outputs["csv"].exists()
    assert score_outputs["report"].exists()
