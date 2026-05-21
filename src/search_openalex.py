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
    abstract_from_inverted_index,
    author_names,
    clean_text,
    env,
    ensure_dirs,
    load_queries,
    now_iso,
    request_json,
    result_row,
    write_csv,
    write_results_csv,
)


OPENALEX_WORKS_URL = "https://api.openalex.org/works"


def query_specs(config: dict[str, Any], selected: set[str] | None = None) -> list[dict[str, Any]]:
    metadata = config.get("metadata", {})
    specs: list[dict[str, Any]] = []
    for direction in config["directions"]:
        direction_id = str(direction["id"])
        if selected and direction_id not in selected:
            continue
        for index, query in enumerate(direction["queries"], start=1):
            specs.append(
                {
                    "direction_id": direction_id,
                    "direction_zh": direction.get("zh") or direction.get("name") or direction_id,
                    "direction_name_en": direction.get("name_en", direction.get("name", direction_id)),
                    "query_label": f"{direction_id.lower()}_{index}",
                    "query": str(query),
                    "from_year": metadata.get("default_from_year", 1990),
                    "to_year": metadata.get("default_to_year"),
                }
            )
    return specs


def openalex_params(spec: dict[str, Any], cursor: str, per_page: int, from_year: int | None, to_year: int | None) -> dict[str, Any]:
    start_year = from_year or int(spec.get("from_year") or 1990)
    end_year = to_year or spec.get("to_year")
    filters = [f"from_publication_date:{start_year}-01-01"]
    if end_year:
        filters.append(f"to_publication_date:{int(end_year)}-12-31")
    params: dict[str, Any] = {
        "search": spec["query"],
        "filter": ",".join(filters),
        "per-page": per_page,
        "cursor": cursor,
        "sort": "relevance_score:desc",
    }
    if env("CONTACT_EMAIL"):
        params["mailto"] = env("CONTACT_EMAIL")
    if env("OPENALEX_API_KEY"):
        params["api_key"] = env("OPENALEX_API_KEY")
    return params


def normalize_openalex_result(record: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    primary_location = record.get("primary_location") if isinstance(record.get("primary_location"), dict) else {}
    source = primary_location.get("source") if isinstance(primary_location.get("source"), dict) else {}
    best_oa = record.get("best_oa_location") if isinstance(record.get("best_oa_location"), dict) else {}
    authors = []
    for authorship in record.get("authorships") or []:
        author = authorship.get("author") if isinstance(authorship, dict) else {}
        if isinstance(author, dict):
            authors.append({"name": author.get("display_name")})
    return result_row(
        direction=spec["direction_id"],
        direction_zh=spec["direction_zh"],
        query=spec["query"],
        title=record.get("title") or record.get("display_name"),
        year=record.get("publication_year"),
        authors=author_names(authors),
        venue=source.get("display_name"),
        doi=record.get("doi"),
        url=primary_location.get("landing_page_url") or record.get("doi") or record.get("id"),
        abstract=abstract_from_inverted_index(record.get("abstract_inverted_index")),
        citation_count=record.get("cited_by_count"),
        source_database="OpenAlex",
        open_access_pdf=best_oa.get("pdf_url") or primary_location.get("pdf_url") or UNCLEAR,
        raw_id=record.get("id"),
    )


def run_search(
    queries_path: Path = QUERIES_PATH,
    raw_dir: Path = DATA_RAW,
    processed_dir: Path = DATA_PROCESSED,
    selected_directions: set[str] | None = None,
    per_query: int = 50,
    max_pages: int | None = None,
    from_year: int | None = None,
    to_year: int | None = None,
    dry_run: bool = False,
) -> dict[str, Path]:
    ensure_dirs()
    config = load_queries(queries_path)
    specs = query_specs(config, selected_directions)
    per_query = max(per_query, 50)
    per_page = min(max(per_query, 50), 200)
    if dry_run:
        plan_path = processed_dir / "openalex_query_plan.csv"
        write_csv(plan_path, specs)
        print(f"dry-run: wrote {plan_path} with {len(specs)} query specs")
        return {"query_plan": plan_path}

    results: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    pause = float(config.get("metadata", {}).get("request_pause_seconds", 0.8))
    for spec in tqdm(specs, desc="OpenAlex queries"):
        cursor = "*"
        fetched_for_query = 0
        status_code: str | int = UNCLEAR
        error = UNCLEAR
        page_limit = max_pages or max(1, (per_query + per_page - 1) // per_page)
        for _ in range(page_limit):
            payload, audit = request_json(
                OPENALEX_WORKS_URL,
                params=openalex_params(spec, cursor, per_page, from_year, to_year),
                pause_seconds=pause,
            )
            status_code = audit["status_code"]
            error = audit["error"]
            if not audit["ok"] or not isinstance(payload, dict):
                break
            records = [record for record in payload.get("results", []) or [] if isinstance(record, dict)]
            for record in records:
                if fetched_for_query >= per_query:
                    break
                results.append(normalize_openalex_result(record, spec))
                fetched_for_query += 1
            cursor = clean_text((payload.get("meta") or {}).get("next_cursor"))
            if fetched_for_query >= per_query or cursor == UNCLEAR or not records:
                break
        audit_rows.append(
            {
                "source_database": "OpenAlex",
                "direction": spec["direction_id"],
                "direction_zh": spec["direction_zh"],
                "query": spec["query"],
                "records_fetched": fetched_for_query,
                "status_code": status_code,
                "error": error,
                "retrieved_at": now_iso(),
            }
        )

    csv_path = raw_dir / "openalex_results.csv"
    audit_path = processed_dir / "openalex_audit.csv"
    write_results_csv(csv_path, results)
    write_csv(audit_path, audit_rows)
    print(f"OpenAlex 检索到论文数量: {len(results)}")
    print(f"wrote {csv_path}")
    return {"csv": csv_path, "audit": audit_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Search OpenAlex for every query in queries.yaml.")
    parser.add_argument("--queries", type=Path, default=QUERIES_PATH)
    parser.add_argument("--directions", default="", help="Comma-separated direction ids, e.g. A,B,D")
    parser.add_argument("--per-query", type=int, default=50, help="Results per query; values below 50 are clamped to 50.")
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--from-year", type=int, default=None)
    parser.add_argument("--to-year", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    selected = {item.strip() for item in args.directions.split(",") if item.strip()} or None
    run_search(
        queries_path=args.queries,
        selected_directions=selected,
        per_query=args.per_query,
        max_pages=args.max_pages,
        from_year=args.from_year,
        to_year=args.to_year,
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
