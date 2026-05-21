from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

import search_crossref  # noqa: E402
import search_openalex  # noqa: E402
import search_semantic_scholar  # noqa: E402


REQUIRED_COLUMNS = [
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


def test_openalex_query_search_writes_required_raw_csv(tmp_path: Path, monkeypatch) -> None:
    def fake_request_json(*args, **kwargs):
        return {
            "results": [
                {
                    "id": "https://openalex.org/W1",
                    "title": "OpenAlex Paper",
                    "publication_year": 2024,
                    "doi": "https://doi.org/10.1/openalex",
                    "authorships": [{"author": {"display_name": "Alice"}}],
                    "primary_location": {
                        "landing_page_url": "https://example.org/openalex",
                        "source": {"display_name": "Journal A"},
                    },
                    "best_oa_location": {"pdf_url": "https://example.org/a.pdf"},
                    "abstract_inverted_index": {"Carbonation": [0]},
                    "cited_by_count": 7,
                }
            ],
            "meta": {"next_cursor": None},
        }, {"ok": True, "status_code": 200, "error": "unclear", "retrieved_at": "now"}

    monkeypatch.setattr(search_openalex, "request_json", fake_request_json)
    outputs = search_openalex.run_search(raw_dir=tmp_path, processed_dir=tmp_path, per_query=50, max_pages=1, selected_directions={"A"})

    frame = pd.read_csv(outputs["csv"])
    assert list(frame.columns) == REQUIRED_COLUMNS
    assert len(frame) == 10
    assert frame.iloc[0]["direction"] == "A"
    assert frame.iloc[0]["source_database"] == "OpenAlex"


def test_semantic_scholar_query_search_writes_required_raw_csv(tmp_path: Path, monkeypatch) -> None:
    def fake_request_json(*args, **kwargs):
        return {
            "data": [
                {
                    "paperId": "S2-1",
                    "title": "Semantic Scholar Paper",
                    "year": 2023,
                    "authors": [{"name": "Bob"}],
                    "venue": "Journal B",
                    "externalIds": {"DOI": "10.1/s2"},
                    "url": "https://example.org/s2",
                    "abstract": None,
                    "citationCount": 5,
                    "openAccessPdf": {"url": "https://example.org/s2.pdf"},
                }
            ]
        }, {"ok": True, "status_code": 200, "error": "unclear", "retrieved_at": "now"}

    monkeypatch.setattr(search_semantic_scholar, "request_json", fake_request_json)
    outputs = search_semantic_scholar.run_search(raw_dir=tmp_path, processed_dir=tmp_path, per_query=50, selected_directions={"B"})

    frame = pd.read_csv(outputs["csv"])
    assert list(frame.columns) == REQUIRED_COLUMNS
    assert len(frame) == 10
    assert frame.iloc[0]["direction_zh"] == "离心/超重力成型混凝土"
    assert frame.iloc[0]["abstract"] == "unclear"


def test_crossref_query_search_writes_required_raw_csv(tmp_path: Path, monkeypatch) -> None:
    def fake_request_json(*args, **kwargs):
        return {
            "message": {
                "items": [
                    {
                        "DOI": "10.1/crossref",
                        "title": ["Crossref Paper"],
                        "published-print": {"date-parts": [[2022]]},
                        "author": [{"given": "Carol", "family": "Chen"}],
                        "container-title": ["Journal C"],
                        "URL": "https://example.org/crossref",
                        "abstract": "<jats:p>Crossref abstract</jats:p>",
                        "is-referenced-by-count": 3,
                        "link": [{"content-type": "application/pdf", "URL": "https://example.org/c.pdf"}],
                    }
                ]
            }
        }, {"ok": True, "status_code": 200, "error": "unclear", "retrieved_at": "now"}

    monkeypatch.setattr(search_crossref, "request_json", fake_request_json)
    outputs = search_crossref.run_search(raw_dir=tmp_path, processed_dir=tmp_path, per_query=50, selected_directions={"C"})

    frame = pd.read_csv(outputs["csv"])
    assert list(frame.columns) == REQUIRED_COLUMNS
    assert len(frame) == 10
    assert frame.iloc[0]["authors"] == "Carol Chen"
    assert frame.iloc[0]["source_database"] == "Crossref"
