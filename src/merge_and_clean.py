from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from rapidfuzz import fuzz
except Exception:  # noqa: BLE001
    from difflib import SequenceMatcher

    class fuzz:  # type: ignore[no-redef]
        @staticmethod
        def token_set_ratio(a: str, b: str) -> float:
            return SequenceMatcher(None, a, b).ratio() * 100

from common import (
    DATA_PROCESSED,
    DATA_RAW,
    FIGURES,
    REPORTS,
    RESULT_COLUMNS,
    UNCLEAR,
    clean_text,
    ensure_dirs,
    is_unclear,
    normalize_doi,
    read_csv,
    safe_int,
    title_key,
    write_csv,
)


RAW_INPUTS = {
    "OpenAlex": "openalex_results.csv",
    "Semantic Scholar": "semantic_scholar_results.csv",
    "Crossref": "crossref_results.csv",
}

MASTER_COLUMNS = RESULT_COLUMNS + [
    "duplicate_count",
    "duplicate_sources",
    "duplicate_queries",
    "direction_labels",
    "direction_names",
    "matched_query",
    "cited_by_count",
    "source",
]


def sample_records() -> list[dict[str, Any]]:
    return [
        {
            "direction": "A",
            "direction_zh": "超重力碳化固废",
            "query": '"rotating packed bed" mineral carbonation',
            "title": "Rotating packed bed mineral carbonation of steel slag",
            "year": "2024",
            "authors": "Li Wei",
            "venue": "Journal of Cleaner Production",
            "doi": "https://doi.org/10.1000/RPB",
            "url": "https://example.org/rpb",
            "abstract": "High gravity mineral carbonation of BOF slag.",
            "citation_count": "12",
            "source_database": "OpenAlex",
            "open_access_pdf": "",
            "raw_id": "W1",
        },
        {
            "direction": "A",
            "direction_zh": "超重力碳化固废",
            "query": '"steel slag" "CO2 mineralization"',
            "title": "Rotating packed bed mineral carbonation of steel slag",
            "year": "2024",
            "authors": "Li Wei; Zhang Min",
            "venue": "Journal of Cleaner Production",
            "doi": "10.1000/rpb",
            "url": "https://example.org/rpb-s2",
            "abstract": "High gravity mineral carbonation of steel slag with a longer abstract.",
            "citation_count": "18",
            "source_database": "Semantic Scholar",
            "open_access_pdf": "https://example.org/rpb.pdf",
            "raw_id": "S1",
        },
        {
            "direction": "D",
            "direction_zh": "CO2养护与碳化混凝土",
            "query": '"accelerated carbonation curing" concrete',
            "title": "Accelerated carbonation curing of concrete",
            "year": "2022",
            "authors": "Jane Doe",
            "venue": "Cement and Concrete Research",
            "doi": "",
            "url": "https://example.org/co2",
            "abstract": "CO2 curing improves early strength.",
            "citation_count": "45",
            "source_database": "Crossref",
            "open_access_pdf": "",
            "raw_id": "C1",
        },
        {
            "direction": "B",
            "direction_zh": "离心/超重力成型混凝土",
            "query": '"spun concrete" pipe pile',
            "title": "Spun concrete pipe piles under flexure",
            "year": "2020",
            "authors": "",
            "venue": "Construction and Building Materials",
            "doi": "10.1000/spun",
            "url": "https://example.org/spun",
            "abstract": "Centrifugal forming changes concrete distribution.",
            "citation_count": "9",
            "source_database": "OpenAlex",
            "open_access_pdf": "",
            "raw_id": "W3",
        },
    ]


def load_raw_csv_records(raw_dir: Path = DATA_RAW) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    raw_by_database = {database: 0 for database in RAW_INPUTS}
    missing_files: list[str] = []

    for database, filename in RAW_INPUTS.items():
        path = raw_dir / filename
        if not path.exists():
            missing_files.append(filename)
            continue
        frame = read_csv(path)
        if frame.empty:
            raw_by_database[database] = 0
            continue
        rows = frame.to_dict(orient="records")
        for row in rows:
            if is_unclear(row.get("source_database")):
                row["source_database"] = database
        raw_by_database[database] = len(rows)
        records.extend(rows)

    return records, {
        "raw_by_database": raw_by_database,
        "missing_files": missing_files,
        "raw_record_count": len(records),
    }


def normalize_raw_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {column: UNCLEAR for column in RESULT_COLUMNS}
    for column in RESULT_COLUMNS:
        normalized[column] = clean_text(row.get(column))
    normalized["title"] = clean_text(normalized["title"])
    normalized["doi"] = normalize_doi(normalized["doi"])
    normalized["authors"] = normalized["authors"] if not is_unclear(normalized["authors"]) else UNCLEAR
    normalized["year"] = normalize_year(normalized["year"])
    normalized["citation_count"] = normalize_citation_count(normalized["citation_count"])
    return normalized


def normalize_year(value: Any) -> int | str:
    year = safe_int(value)
    if year is None:
        return UNCLEAR
    return year


def normalize_citation_count(value: Any) -> int | str:
    citation_count = safe_int(value)
    if citation_count is None:
        return UNCLEAR
    return max(citation_count, 0)


def is_valid_year(value: Any) -> bool:
    if is_unclear(value):
        return True
    year = safe_int(value)
    if year is None:
        return False
    return 1800 <= year <= datetime.now().year + 1


def clean_records(records: list[dict[str, Any]], title_similarity_threshold: int = 95) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stats: dict[str, Any] = {
        "raw_record_count": len(records),
        "dropped_empty_title": 0,
        "dropped_invalid_year": 0,
        "raw_by_database": {database: 0 for database in RAW_INPUTS},
    }

    cleaned_rows: list[dict[str, Any]] = []
    for record in records:
        source_database = clean_text(record.get("source_database"))
        if source_database in stats["raw_by_database"]:
            stats["raw_by_database"][source_database] += 1
        row = normalize_raw_row(record)
        if is_unclear(row["title"]):
            stats["dropped_empty_title"] += 1
            continue
        if not is_valid_year(row["year"]):
            stats["dropped_invalid_year"] += 1
            continue
        cleaned_rows.append(row)

    groups = group_records(cleaned_rows, title_similarity_threshold)
    merged_rows = [merge_group(group) for group in groups]
    for index, row in enumerate(merged_rows, start=1):
        row["duplicate_group_id"] = f"G{index:05d}"

    stats["after_cleaning_count"] = len(cleaned_rows)
    stats["deduped_record_count"] = len(merged_rows)
    stats["direction_counts"] = count_values(merged_rows, "direction")
    stats["database_contribution"] = count_values(merged_rows, "source_database")
    stats["missing_doi_count"] = sum(1 for row in merged_rows if is_unclear(row.get("doi")))
    stats["missing_abstract_count"] = sum(1 for row in merged_rows if is_unclear(row.get("abstract")))
    stats["missing_doi_ratio"] = ratio(stats["missing_doi_count"], len(merged_rows))
    stats["missing_abstract_ratio"] = ratio(stats["missing_abstract_count"], len(merged_rows))
    return merged_rows, stats


def group_records(rows: list[dict[str, Any]], title_similarity_threshold: int) -> list[list[dict[str, Any]]]:
    doi_groups: dict[str, list[dict[str, Any]]] = {}
    title_groups: list[list[dict[str, Any]]] = []

    for row in rows:
        doi = normalize_doi(row.get("doi"))
        if doi != UNCLEAR:
            doi_groups.setdefault(doi, []).append(row)
            continue
        title = title_key(row.get("title"))
        placed = False
        for group in title_groups:
            representative = title_key(group[0].get("title"))
            if title != UNCLEAR and representative != UNCLEAR and fuzz.token_set_ratio(title, representative) >= title_similarity_threshold:
                group.append(row)
                placed = True
                break
        if not placed:
            title_groups.append([row])

    return list(doi_groups.values()) + title_groups


def merge_group(group: list[dict[str, Any]]) -> dict[str, Any]:
    winner = max(group, key=record_quality)
    merged = dict(winner)
    sources = sorted({row["source_database"] for row in group if not is_unclear(row.get("source_database"))})
    queries = sorted({row["query"] for row in group if not is_unclear(row.get("query"))})
    directions = sorted({row["direction"] for row in group if not is_unclear(row.get("direction"))})
    direction_names = sorted({row["direction_zh"] for row in group if not is_unclear(row.get("direction_zh"))})

    merged["duplicate_count"] = len(group)
    merged["duplicate_sources"] = "|".join(sources) if sources else UNCLEAR
    merged["duplicate_queries"] = "|".join(queries) if queries else UNCLEAR
    merged["direction"] = "|".join(directions) if directions else merged.get("direction", UNCLEAR)
    merged["direction_zh"] = "|".join(direction_names) if direction_names else merged.get("direction_zh", UNCLEAR)
    merged["query"] = "|".join(queries) if queries else merged.get("query", UNCLEAR)
    merged["direction_labels"] = merged["direction"]
    merged["direction_names"] = merged["direction_zh"]
    merged["matched_query"] = merged["query"]
    merged["cited_by_count"] = merged["citation_count"]
    merged["source"] = merged["source_database"]
    return {column: merged.get(column, UNCLEAR) for column in MASTER_COLUMNS}


def record_quality(row: dict[str, Any]) -> tuple[int, int, int]:
    citation_count = safe_int(row.get("citation_count")) or 0
    abstract_length = 0 if is_unclear(row.get("abstract")) else len(str(row["abstract"]))
    filled = sum(1 for value in row.values() if not is_unclear(value))
    return citation_count, abstract_length, filled


def count_values(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = clean_text(row.get(field))
        if value == UNCLEAR:
            value = "unclear"
        for item in str(value).split("|"):
            key = item.strip() or "unclear"
            counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def uncertainty_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tracked_fields = ["doi", "authors", "venue", "abstract", "citation_count", "open_access_pdf"]
    output = []
    for index, row in enumerate(rows):
        for field in tracked_fields:
            if is_unclear(row.get(field)):
                output.append(
                    {
                        "row_index": index,
                        "title": row.get("title", UNCLEAR),
                        "field": field,
                        "value": UNCLEAR,
                    }
                )
    return output


def write_cleaning_report(path: Path, stats: dict[str, Any], outputs: dict[str, Path]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_by_database = stats.get("raw_by_database", {})
    direction_counts = stats.get("direction_counts", {})
    database_contribution = stats.get("database_contribution", {})
    missing_files = stats.get("missing_files", [])

    lines = [
        "# 清洗报告",
        "",
        "## 总览",
        "",
        f"- 原始记录数：{stats.get('raw_record_count', 0)}",
        f"- 清洗后记录数：{stats.get('after_cleaning_count', 0)}",
        f"- 去重后记录数：{stats.get('deduped_record_count', 0)}",
        f"- 删除空标题记录数：{stats.get('dropped_empty_title', 0)}",
        f"- 删除异常年份记录数：{stats.get('dropped_invalid_year', 0)}",
        f"- 缺失 DOI 比例：{stats.get('missing_doi_ratio', 0):.2%}",
        f"- 缺失摘要比例：{stats.get('missing_abstract_ratio', 0):.2%}",
        "",
        "## 原始记录数（按数据库）",
        "",
    ]
    lines.extend(f"- {database}: {count}" for database, count in raw_by_database.items())
    if missing_files:
        lines.extend(["", "## 缺失输入文件", ""])
        lines.extend(f"- {filename}" for filename in missing_files)
    lines.extend(["", "## 每个方向剩余论文数", ""])
    lines.extend(f"- {direction}: {count}" for direction, count in direction_counts.items())
    lines.extend(["", "## 每个数据库贡献记录数（去重后主记录来源）", ""])
    lines.extend(f"- {database}: {count}" for database, count in database_contribution.items())
    lines.extend(["", "## 输出文件", ""])
    for label, output_path in outputs.items():
        lines.append(f"- {label}: `{output_path}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run_merge(
    raw_dir: Path = DATA_RAW,
    processed_dir: Path = DATA_PROCESSED,
    reports_dir: Path = REPORTS,
    sample: bool = False,
    title_similarity_threshold: int = 95,
) -> dict[str, Path]:
    ensure_dirs()
    reports_dir.mkdir(parents=True, exist_ok=True)
    if sample:
        records = sample_records()
        load_stats = {
            "raw_by_database": count_values(records, "source_database"),
            "missing_files": [],
            "raw_record_count": len(records),
        }
    else:
        records, load_stats = load_raw_csv_records(raw_dir)

    cleaned, stats = clean_records(records, title_similarity_threshold=title_similarity_threshold)
    stats["raw_by_database"] = load_stats.get("raw_by_database", stats["raw_by_database"])
    stats["missing_files"] = load_stats.get("missing_files", [])
    stats["raw_record_count"] = load_stats.get("raw_record_count", len(records))

    papers_path = processed_dir / "papers_master.csv"
    works_path = processed_dir / "works_master.csv"
    uncertainty_path = processed_dir / "uncertainty_log.csv"
    report_path = reports_dir / "cleaning_report.md"

    frame = pd.DataFrame(cleaned, columns=MASTER_COLUMNS)
    write_csv(papers_path, frame)
    write_csv(works_path, frame)
    write_csv(uncertainty_path, uncertainty_rows(cleaned))
    outputs = {
        "papers_master": papers_path,
        "works_master": works_path,
        "uncertainty_log": uncertainty_path,
    }
    write_cleaning_report(report_path, stats, outputs)
    print(f"原始记录数: {stats['raw_record_count']}")
    print(f"去重后记录数: {stats['deduped_record_count']}")
    print(f"wrote {papers_path}")
    print(f"wrote {works_path}")
    print(f"wrote {report_path}")
    return {"papers": papers_path, "works": works_path, "uncertainty": uncertainty_path, "report": report_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge, clean, and deduplicate raw literature CSV files.")
    parser.add_argument("--sample", action="store_true", help="Use built-in sample records instead of data/raw CSV files.")
    parser.add_argument("--title-threshold", type=int, default=95, help="Rapidfuzz token_set_ratio threshold for title dedupe when DOI is missing.")
    args = parser.parse_args()
    run_merge(sample=args.sample, title_similarity_threshold=args.title_threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
