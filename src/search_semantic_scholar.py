from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from tqdm import tqdm

from common import (
    DATA_PROCESSED,
    DATA_RAW,
    QUERIES_PATH,
    UNCLEAR,
    author_names,
    env,
    ensure_dirs,
    load_queries,
    now_iso,
    request_json,
    result_row,
    write_csv,
    write_results_csv,
)
from search_openalex import query_specs


BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "paperId,title,year,authors,venue,externalIds,url,abstract,citationCount,openAccessPdf"


def normalize_semantic_scholar_result(record: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    external_ids = record.get("externalIds") if isinstance(record.get("externalIds"), dict) else {}
    open_access_pdf = record.get("openAccessPdf") if isinstance(record.get("openAccessPdf"), dict) else {}
    return result_row(
        direction=spec["direction_id"],
        direction_zh=spec["direction_zh"],
        query=spec["query"],
        title=record.get("title"),
        year=record.get("year"),
        authors=author_names(record.get("authors")),
        venue=record.get("venue"),
        doi=external_ids.get("DOI"),
        url=record.get("url"),
        abstract=record.get("abstract"),
        citation_count=record.get("citationCount"),
        source_database="Semantic Scholar",
        open_access_pdf=open_access_pdf.get("url") or UNCLEAR,
        raw_id=record.get("paperId"),
    )


def run_search(
    queries_path: Path = QUERIES_PATH,
    raw_dir: Path = DATA_RAW,
    processed_dir: Path = DATA_PROCESSED,
    selected_directions: set[str] | None = None,
    per_query: int = 50,
    dry_run: bool = False,
) -> dict[str, Path]:
    ensure_dirs()
    config = load_queries(queries_path)
    specs = query_specs(config, selected_directions)
    per_query = max(per_query, 50)
    if dry_run:
        plan_path = processed_dir / "semantic_scholar_query_plan.csv"
        write_csv(plan_path, specs)
        print(f"dry-run: wrote {plan_path} with {len(specs)} query specs")
        return {"query_plan": plan_path}

    headers = {"User-Agent": "hypergravity-concrete-scout/0.1"}
    if env("SEMANTIC_SCHOLAR_API_KEY"):
        headers["x-api-key"] = env("SEMANTIC_SCHOLAR_API_KEY")

    results: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    pause = float(config.get("metadata", {}).get("request_pause_seconds", 0.8))
    for spec in tqdm(specs, desc="Semantic Scholar queries"):
        payload, audit = request_json(
            BASE_URL,
            params={"query": spec["query"], "limit": per_query, "fields": FIELDS},
            headers=headers,
            pause_seconds=pause,
        )
        query_count = 0
        if audit["status_code"] == 429:
            print("Semantic Scholar rate limit reached. Consider setting SEMANTIC_SCHOLAR_API_KEY or increasing request_pause_seconds.")
        if audit["ok"] and isinstance(payload, dict):
            for record in payload.get("data", []) or []:
                if isinstance(record, dict):
                    results.append(normalize_semantic_scholar_result(record, spec))
                    query_count += 1
        audit_rows.append(
            {
                "source_database": "Semantic Scholar",
                "direction": spec["direction_id"],
                "direction_zh": spec["direction_zh"],
                "query": spec["query"],
                "records_fetched": query_count,
                "status_code": audit["status_code"],
                "error": audit["error"],
                "retrieved_at": now_iso(),
            }
        )

    csv_path = raw_dir / "semantic_scholar_results.csv"
    audit_path = processed_dir / "semantic_scholar_audit.csv"
    write_results_csv(csv_path, results)
    write_csv(audit_path, audit_rows)
    print(f"Semantic Scholar 检索到论文数量: {len(results)}")
    print(f"wrote {csv_path}")
    return {"csv": csv_path, "audit": audit_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Semantic Scholar for every query in queries.yaml.")
    parser.add_argument("--queries", type=Path, default=QUERIES_PATH)
    parser.add_argument("--directions", default="", help="Comma-separated direction ids, e.g. A,B,D")
    parser.add_argument("--per-query", type=int, default=50, help="Results per query; values below 50 are clamped to 50.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    selected = {item.strip() for item in args.directions.split(",") if item.strip()} or None
    run_search(queries_path=args.queries, selected_directions=selected, per_query=args.per_query, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
