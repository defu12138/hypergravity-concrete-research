from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from score_directions import score_directions  # noqa: E402


def test_score_directions_outputs_scores_report_and_recommendation_groups(tmp_path: Path) -> None:
    processed = tmp_path / "data" / "processed"
    reports = tmp_path / "reports"
    processed.mkdir(parents=True)
    reports.mkdir()
    papers = []
    for direction in ["A", "B", "C", "D", "E", "F"]:
        for index, year in enumerate([2025, 2024, 2023, 2022, 2021, 2020], start=1):
            papers.append(
                {
                    "direction": direction,
                    "title": f"{direction} concrete carbonation paper {index}",
                    "year": year,
                    "authors": "Author",
                    "venue": "Journal",
                    "doi": f"10/{direction}{index}",
                    "url": "https://example.org",
                    "abstract": "cement concrete carbonation rotating packed bed",
                    "citation_count": 100 - index,
                    "source_database": "OpenAlex",
                    "query": "concrete carbonation",
                }
            )
    pd.DataFrame(papers).to_csv(processed / "papers_master.csv", index=False)
    pd.DataFrame(papers[:18]).to_csv(processed / "reading_list_by_direction.csv", index=False)
    report_path = reports / "landscape_summary.md"
    report_path.write_text("# landscape\n\n## A\n\n活跃。\n", encoding="utf-8")
    queries_path = tmp_path / "queries.yaml"
    queries_path.write_text(
        yaml.safe_dump({"directions": [{"id": item, "zh": f"方向{item}", "note_zh": f"note {item}"} for item in ["A", "B", "C", "D", "E", "F"]]}, allow_unicode=True),
        encoding="utf-8",
    )

    outputs = score_directions(processed_dir=processed, reports_dir=reports, queries_path=queries_path)

    assert outputs["csv"].exists()
    assert outputs["report"].exists()
    scores = pd.read_csv(outputs["csv"])
    expected_columns = {
        "direction",
        "direction_zh",
        "overall_score",
        "literature_heat",
        "maturity",
        "novelty_space",
        "experimental_feasibility",
        "equipment_accessibility",
        "concrete_relevance",
        "publication_potential",
        "recommendation_group",
        "main_risk_cn",
        "score_explanation_cn",
    }
    assert expected_columns.issubset(scores.columns)
    assert scores["overall_score"].between(0, 5).all()
    report = outputs["report"].read_text(encoding="utf-8")
    assert "主攻方向" in report
    assert "备用方向" in report
    assert "暂缓方向" in report
    assert "主要风险" in report
