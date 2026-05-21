from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from merge_and_clean import clean_records, load_raw_csv_records, run_merge  # noqa: E402


def write_raw_csv(path: Path, rows: list[dict[str, object]]) -> None:
    columns = [
        "direction",
        "direction_zh",
        "query",
        "title",
        "year",
        "authors",
        "venue",
        "doi",
        "url",
        "abstract",
        "citation_count",
        "source_database",
        "open_access_pdf",
        "raw_id",
    ]
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)


def test_load_raw_csv_records_tolerates_missing_database_files(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    write_raw_csv(
        raw_dir / "openalex_results.csv",
        [
            {
                "direction": "A",
                "direction_zh": "超重力碳化固废",
                "query": '"high gravity" carbonation steel slag',
                "title": " A paper ",
                "year": 2024,
                "authors": "",
                "venue": "Journal A",
                "doi": "https://doi.org/10.1/ABC",
                "url": "https://example.org/a",
                "abstract": "Short abstract.",
                "citation_count": 2,
                "source_database": "OpenAlex",
                "open_access_pdf": "",
                "raw_id": "W1",
            }
        ],
    )

    records, stats = load_raw_csv_records(raw_dir)

    assert len(records) == 1
    assert stats["raw_by_database"]["OpenAlex"] == 1
    assert stats["raw_by_database"]["Semantic Scholar"] == 0
    assert stats["raw_by_database"]["Crossref"] == 0


def test_clean_records_filters_normalizes_and_dedupes_by_doi_and_title() -> None:
    records = [
        {
            "direction": "A",
            "direction_zh": "超重力碳化固废",
            "query": "q1",
            "title": "Steel slag carbonation\npaper",
            "year": "2024",
            "authors": "",
            "venue": "Journal A",
            "doi": "https://doi.org/10.1/ABC",
            "url": "https://example.org/a",
            "abstract": "Short.",
            "citation_count": "1",
            "source_database": "OpenAlex",
            "open_access_pdf": "",
            "raw_id": "W1",
        },
        {
            "direction": "A",
            "direction_zh": "超重力碳化固废",
            "query": "q2",
            "title": "Steel slag carbonation paper",
            "year": "2024",
            "authors": "Li Wei",
            "venue": "Journal A",
            "doi": "10.1/abc",
            "url": "https://example.org/a2",
            "abstract": "This is a much longer abstract for the same DOI.",
            "citation_count": "9",
            "source_database": "Semantic Scholar",
            "open_access_pdf": "https://example.org/a.pdf",
            "raw_id": "S1",
        },
        {
            "direction": "D",
            "direction_zh": "CO2养护与碳化混凝土",
            "query": "q3",
            "title": "Carbonation curing concrete strength",
            "year": "2022",
            "authors": "Jane Doe",
            "venue": "Journal D",
            "doi": "",
            "url": "https://example.org/d",
            "abstract": "Useful abstract.",
            "citation_count": "5",
            "source_database": "Crossref",
            "open_access_pdf": "",
            "raw_id": "C1",
        },
        {
            "direction": "D",
            "direction_zh": "CO2养护与碳化混凝土",
            "query": "q4",
            "title": "Carbonation curing: concrete strength",
            "year": "2022",
            "authors": "Jane Doe",
            "venue": "Journal D",
            "doi": "",
            "url": "https://example.org/d2",
            "abstract": "Longer useful abstract for the title duplicate.",
            "citation_count": "3",
            "source_database": "OpenAlex",
            "open_access_pdf": "",
            "raw_id": "W2",
        },
        {
            "direction": "B",
            "direction_zh": "离心/超重力成型混凝土",
            "query": "q5",
            "title": "",
            "year": "2020",
            "authors": "No Title",
            "venue": "Journal B",
            "doi": "10.1/badtitle",
            "url": "",
            "abstract": "",
            "citation_count": "0",
            "source_database": "OpenAlex",
            "open_access_pdf": "",
            "raw_id": "bad-title",
        },
        {
            "direction": "C",
            "direction_zh": "重力场对水泥水化影响",
            "query": "q6",
            "title": "Impossible year paper",
            "year": "3020",
            "authors": "Bad Year",
            "venue": "Journal C",
            "doi": "10.1/badyear",
            "url": "",
            "abstract": "",
            "citation_count": "0",
            "source_database": "OpenAlex",
            "open_access_pdf": "",
            "raw_id": "bad-year",
        },
    ]

    cleaned, stats = clean_records(records)

    frame = pd.DataFrame(cleaned)
    assert len(frame) == 2
    assert stats["dropped_empty_title"] == 1
    assert stats["dropped_invalid_year"] == 1
    doi_row = frame[frame["doi"] == "10.1/abc"].iloc[0]
    assert doi_row["citation_count"] == 9
    assert doi_row["authors"] == "Li Wei"
    assert doi_row["duplicate_sources"] == "OpenAlex|Semantic Scholar"
    assert "q1" in doi_row["duplicate_queries"]
    title_row = frame[frame["doi"] == "unclear"].iloc[0]
    assert title_row["duplicate_count"] == 2
    assert title_row["abstract"] == "Useful abstract."


def test_run_merge_writes_master_files_and_cleaning_report(tmp_path: Path) -> None:
    raw_dir = tmp_path / "data" / "raw"
    processed_dir = tmp_path / "data" / "processed"
    reports_dir = tmp_path / "reports"
    raw_dir.mkdir(parents=True)
    write_raw_csv(
        raw_dir / "openalex_results.csv",
        [
            {
                "direction": "A",
                "direction_zh": "超重力碳化固废",
                "query": "q",
                "title": "Report Paper",
                "year": "2024",
                "authors": "",
                "venue": "Journal",
                "doi": "",
                "url": "",
                "abstract": "",
                "citation_count": "1",
                "source_database": "OpenAlex",
                "open_access_pdf": "",
                "raw_id": "W1",
            }
        ],
    )

    outputs = run_merge(raw_dir=raw_dir, processed_dir=processed_dir, reports_dir=reports_dir)

    assert outputs["papers"].exists()
    assert outputs["works"].exists()
    assert outputs["report"].exists()
    report = outputs["report"].read_text(encoding="utf-8")
    assert "原始记录数" in report
    assert "缺失 DOI" in report
