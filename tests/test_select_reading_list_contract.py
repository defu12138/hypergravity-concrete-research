from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from select_reading_list import classify_relevance, select_reading_list  # noqa: E402


def test_relevance_classifier_keeps_maybe_and_removes_irrelevant() -> None:
    relevant = classify_relevance({"title": "CO2 curing concrete carbonation", "abstract": "", "query": ""})
    maybe = classify_relevance({"title": "Novel mineralization process", "abstract": "", "query": ""})
    irrelevant = classify_relevance({"title": "Neural network image classification", "abstract": "deep learning", "query": ""})

    assert relevant.status == "relevant"
    assert maybe.status == "maybe_relevant"
    assert irrelevant.status == "irrelevant"


def test_select_reading_list_outputs_direction_lists_with_recent_papers(tmp_path: Path) -> None:
    processed = tmp_path / "data" / "processed"
    reports = tmp_path / "reports"
    processed.mkdir(parents=True)
    reports.mkdir()
    rows = []
    for direction in ["A", "B", "C", "D", "E", "F"]:
        for index, year in enumerate([2025, 2024, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013], start=1):
            rows.append(
                {
                    "direction": direction,
                    "direction_zh": direction,
                    "query": "carbonation concrete",
                    "title": f"{direction} concrete carbonation paper {index}",
                    "year": year,
                    "authors": "Author One; Author Two",
                    "venue": f"Journal {direction}",
                    "doi": f"10.123/{direction.lower()}{index}",
                    "url": f"https://example.org/{direction}/{index}",
                    "abstract": "This paper studies concrete carbonation and cementitious materials.",
                    "citation_count": 100 - index,
                    "source_database": "OpenAlex",
                    "open_access_pdf": "unclear",
                    "raw_id": f"{direction}{index}",
                }
            )
    rows.append(
        {
            "direction": "A",
            "direction_zh": "A",
            "query": "unrelated",
            "title": "Neural network image classification",
            "year": 2025,
            "authors": "Unrelated Author",
            "venue": "AI Journal",
            "doi": "10.unrelated",
            "url": "https://example.org/no",
            "abstract": "deep learning image classification",
            "citation_count": 1000,
            "source_database": "OpenAlex",
            "open_access_pdf": "unclear",
            "raw_id": "bad",
        }
    )
    papers_path = processed / "papers_master.csv"
    top_cited_path = processed / "top_cited_papers.csv"
    pd.DataFrame(rows).to_csv(papers_path, index=False)
    pd.DataFrame(rows).head(30).to_csv(top_cited_path, index=False)
    queries_path = tmp_path / "queries.yaml"
    queries_path.write_text(
        yaml.safe_dump({"directions": [{"id": item, "zh": f"方向{item}"} for item in ["A", "B", "C", "D", "E", "F"]]}, allow_unicode=True),
        encoding="utf-8",
    )

    outputs = select_reading_list(
        papers_path=papers_path,
        top_cited_path=top_cited_path,
        processed_dir=processed,
        reports_dir=reports,
        queries_path=queries_path,
    )

    selected = pd.read_csv(outputs["csv"])
    assert outputs["report"].exists()
    assert list(selected.columns) == [
        "direction",
        "title",
        "year",
        "authors",
        "venue",
        "doi",
        "url",
        "citation_count",
        "abstract",
        "relevance_reason_cn",
        "possible_inspiration_for_my_project_cn",
    ]
    assert "Neural network image classification" not in set(selected["title"])
    assert selected.groupby("direction").size().min() >= 10
    recent = selected[selected["year"] >= 2023].groupby("direction").size()
    assert recent.min() >= 2
    assert "方向A" in outputs["report"].read_text(encoding="utf-8")
