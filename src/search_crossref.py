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
    clean_text,
    env,
    ensure_dirs,
    load_queries,
    now_iso,
    request_json,
    result_row,
    strip_html,
    write_csv,
    write_results_csv,
)
from search_openalex import query_specs


BASE_URL = "https://api.crossref.org/works"


def first(value: Any) -> Any:
    if isinstance(value, list) and value:
        return value[0]
    return value


def crossref_year(record: dict[str, Any]) -> Any:
    for key in ["published-print", "published-online", "published", "issued"]:
        parts = ((record.get(key) or {}).get("date-parts") or []) if isinstance(record.get(key), dict) else []
        if parts and parts[0]:
            return parts[0][0]
    return UNCLEAR


def crossref_authors(record: dict[str, Any]) -> str:
    names = []
    for author in record.get("author", []) or []:
        if not isinstance(author, dict):
            continue
        name = clean_text(f"{author.get('given', '')} {author.get('family', '')}")
        if name != UNCLEAR:
            names.append(name)
    return "; ".join(names) if names else UNCLEAR


def crossref_pdf(record: dict[str, Any]) -> str:
    for link in record.get("link", []) or []:
        if not isinstance(link, dict):
            continue
        content_type = str(link.get("content-type", "")).lower()
        url = clean_text(link.get("URL"))
        if "pdf" in content_type and url != UNCLEAR:
            return url
    return UNCLEAR


def normalize_crossref_result(record: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    return result_row(
        direction=spec["direction_id"],
        direction_zh=spec["direction_zh"],
        query=spec["query"],
        title=first(record.get("title")),
        year=crossref_year(record),
        authors=crossref_authors(record),
        venue=first(record.get("container-title")),
        doi=record.get("DOI"),
        url=record.get("URL"),
        abstract=strip_html(record.get("abstract")),
        citation_count=record.get("is-referenced-by-count"),
        source_database="Crossref",
        open_access_pdf=crossref_pdf(record),
        raw_id=record.get("DOI") or record.get("URL"),
    )


def polite_user_agent() -> str:
    if env("CONTACT_EMAIL"):
        return f"hypergravity-concrete-scout/0.1 (mailto:{env('CONTACT_EMAIL')})"
    return "hypergravity-concrete-scout/0.1"


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
        plan_path = processed_dir / "crossref_query_plan.csv"
        write_csv(plan_path, specs)
        print(f"dry-run: wrote {plan_path} with {len(specs)} query specs")
        return {"query_plan": plan_path}

    headers = {"User-Agent": polite_user_agent()}
    results: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    pause = float(config.get("metadata", {}).get("request_pause_seconds", 0.8))
    for spec in tqdm(specs, desc="Crossref queries"):
        params: dict[str, Any] = {
            "query.bibliographic": spec["query"],
            "rows": per_query,
            "filter": f"from-pub-date:{int(spec.get('from_year') or 1990)}-01-01",
        }
        if env("CONTACT_EMAIL"):
            params["mailto"] = env("CONTACT_EMAIL")
        payload, audit = request_json(BASE_URL, params=params, headers=headers, pause_seconds=pause)
        query_count = 0
        message = payload.get("message") if isinstance(payload, dict) else {}
        if audit["ok"] and isinstance(message, dict):
            for record in message.get("items", []) or []:
                if isinstance(record, dict):
                    results.append(normalize_crossref_result(record, spec))
                    query_count += 1
        audit_rows.append(
            {
                "source_database": "Crossref",
                "direction": spec["direction_id"],
                "direction_zh": spec["direction_zh"],
                "query": spec["query"],
                "records_fetched": query_count,
                "status_code": audit["status_code"],
                "error": audit["error"],
                "retrieved_at": now_iso(),
            }
        )

    csv_path = raw_dir / "crossref_results.csv"
    audit_path = processed_dir / "crossref_audit.csv"
    write_results_csv(csv_path, results)
    write_csv(audit_path, audit_rows)
    print(f"Crossref 检索到论文数量: {len(results)}")
    print(f"wrote {csv_path}")
    return {"csv": csv_path, "audit": audit_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Crossref for every query in queries.yaml.")
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
