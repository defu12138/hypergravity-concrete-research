from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_PROCESSED, QUERIES_PATH, REPORTS, UNCLEAR, clean_text, load_yaml, read_csv, safe_int, write_csv


OUTPUT_COLUMNS = [
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

CORE_RELEVANCE_TERMS = [
    "cement",
    "concrete",
    "cementitious",
    "carbonation",
    "carbonated",
    "co2 curing",
    "carbon dioxide curing",
    "mineral carbonation",
    "steel slag",
    "bof slag",
    "slag",
    "waste concrete",
    "recycled concrete",
    "carbide slag",
    "high gravity",
    "high-gravity",
    "hypergravity",
    "rotating packed bed",
    "process intensification",
    "mass transfer",
    "centrifuged concrete",
    "spun concrete",
    "centrifugal casting",
    "centrifugal concrete",
    "pipe pile",
    "cement hydration",
    "cement paste",
    "microgravity",
]

MAYBE_TERMS = [
    "mineralization",
    "calcium carbonate",
    "precipitation",
    "gas liquid",
    "solid waste",
    "construction material",
    "curing",
    "hydration",
]

IRRELEVANT_TERMS = [
    "neural network",
    "image classification",
    "medical",
    "biomedical",
    "genome",
    "wireless",
    "battery",
    "photovoltaic",
]


@dataclass(frozen=True)
class RelevanceDecision:
    status: str
    reason_cn: str


def load_direction_names(queries_path: Path = QUERIES_PATH) -> dict[str, str]:
    if not queries_path.exists():
        return {}
    data = load_yaml(queries_path)
    names = {}
    for direction in data.get("directions", []) or []:
        if isinstance(direction, dict) and direction.get("id"):
            names[str(direction["id"])] = str(direction.get("zh") or direction.get("name") or direction["id"])
    return names


def split_directions(value: Any) -> list[str]:
    text = clean_text(value)
    if text == UNCLEAR:
        return []
    return [item.strip() for item in text.split("|") if item.strip()]


def text_blob(row: dict[str, Any] | pd.Series) -> str:
    parts = [row.get("title", ""), row.get("abstract", ""), row.get("query", ""), row.get("venue", "")]
    return " ".join(str(part) for part in parts if not pd.isna(part)).lower()


def classify_relevance(row: dict[str, Any] | pd.Series) -> RelevanceDecision:
    blob = text_blob(row)
    matched = [term for term in CORE_RELEVANCE_TERMS if term in blob]
    if matched:
        return RelevanceDecision("relevant", "相关：命中主题关键词：" + "、".join(matched[:5]))
    maybe = [term for term in MAYBE_TERMS if term in blob]
    if maybe:
        return RelevanceDecision("maybe_relevant", "maybe_relevant：仅命中宽泛相关词：" + "、".join(maybe[:5]))
    irrelevant = [term for term in IRRELEVANT_TERMS if term in blob]
    if irrelevant:
        return RelevanceDecision("irrelevant", "明显不相关：命中非本课题词：" + "、".join(irrelevant[:5]))
    return RelevanceDecision("maybe_relevant", "maybe_relevant：题录信息不足，无法可靠判断，保留供人工检查")


def prepare_papers(papers: pd.DataFrame) -> pd.DataFrame:
    frame = papers.copy()
    if "citation_count" not in frame.columns and "cited_by_count" in frame.columns:
        frame["citation_count"] = frame["cited_by_count"]
    if "direction" not in frame.columns and "direction_labels" in frame.columns:
        frame["direction"] = frame["direction_labels"]
    for column in ["direction", "title", "year", "authors", "venue", "doi", "url", "citation_count", "abstract", "query"]:
        if column not in frame.columns:
            frame[column] = UNCLEAR
    frame["year_num"] = frame["year"].map(safe_int)
    frame["citation_num"] = frame["citation_count"].map(lambda value: safe_int(value) or 0)
    decisions = frame.apply(classify_relevance, axis=1)
    frame["relevance_status"] = [decision.status for decision in decisions]
    frame["relevance_reason_cn"] = [decision.reason_cn for decision in decisions]
    return frame


def expand_by_direction(papers: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in papers.iterrows():
        directions = split_directions(row.get("direction"))
        for direction in directions:
            item = row.to_dict()
            item["direction"] = direction
            rows.append(item)
    return pd.DataFrame(rows)


def selection_score(row: pd.Series) -> float:
    citation = safe_int(row.get("citation_count")) or 0
    year = safe_int(row.get("year")) or 0
    recency_bonus = 0
    if year >= 2023:
        recency_bonus = 80
    elif year >= 2018:
        recency_bonus = 40
    relevance_bonus = 30 if row.get("relevance_status") == "relevant" else 10
    return citation + recency_bonus + relevance_bonus


def select_for_direction(group: pd.DataFrame, per_direction: int = 10) -> pd.DataFrame:
    candidates = group[group["relevance_status"] != "irrelevant"].copy()
    if candidates.empty:
        return candidates
    candidates["selection_score"] = candidates.apply(selection_score, axis=1)
    recent = candidates[(candidates["year_num"].fillna(0) >= 2023)].sort_values(["selection_score", "citation_num"], ascending=False).head(2)
    remaining = candidates.drop(index=recent.index, errors="ignore")
    preferred_recent = remaining[remaining["year_num"].fillna(0) >= 2018].sort_values(["selection_score", "citation_num"], ascending=False)
    older = remaining[remaining["year_num"].fillna(0) < 2018].sort_values(["selection_score", "citation_num"], ascending=False)
    selected = pd.concat([recent, preferred_recent, older], ignore_index=False).head(per_direction)
    return selected


def inspiration_cn(row: pd.Series) -> str:
    direction = row.get("direction", UNCLEAR)
    title = clean_text(row.get("title"))
    year = row.get("year", UNCLEAR)
    citations = row.get("citation_count", UNCLEAR)
    if row.get("relevance_status") == "maybe_relevant":
        return f"可作为人工复核候选：题录与方向 {direction} 有弱相关信号，但需要阅读全文判断是否能支撑超重力-混凝土课题。"
    return f"可用于方向 {direction} 的问题定位：结合 {year} 年论文《{title}》的题录和引用数 {citations}，优先检查其方法、材料体系或评价指标是否可迁移到超重力-混凝土研究。"


def build_output_rows(selected: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for _, row in selected.iterrows():
        rows.append(
            {
                "direction": row.get("direction", UNCLEAR),
                "title": row.get("title", UNCLEAR),
                "year": row.get("year", UNCLEAR),
                "authors": row.get("authors", UNCLEAR),
                "venue": row.get("venue", UNCLEAR),
                "doi": row.get("doi", UNCLEAR),
                "url": row.get("url", UNCLEAR),
                "citation_count": row.get("citation_count", UNCLEAR),
                "abstract": row.get("abstract", UNCLEAR),
                "relevance_reason_cn": row.get("relevance_reason_cn", UNCLEAR),
                "possible_inspiration_for_my_project_cn": inspiration_cn(row),
            }
        )
    return rows


def write_report(path: Path, selected: pd.DataFrame, direction_names: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 分方向推荐阅读清单",
        "",
        "本清单基于 `data/processed/papers_master.csv` 和 `data/processed/top_cited_papers.csv` 自动筛选。筛选优先 2018 年以后、高引用论文，并保证每个方向尽量保留至少 2 篇 2023 年以后的新论文；明显无关题录删除，无法判断者标注 maybe_relevant。",
        "",
    ]
    if selected.empty:
        lines.append("unclear: 未筛选到论文。")
    for direction in sorted(selected["direction"].unique()) if not selected.empty else []:
        name = direction_names.get(direction, direction)
        lines.extend([f"## {direction} - {name}", ""])
        subset = selected[selected["direction"] == direction]
        for index, (_, row) in enumerate(subset.iterrows(), start=1):
            lines.extend(
                [
                    f"{index}. **{row['title']}**",
                    f"   - 年份/引用：{row['year']} / {row['citation_count']}",
                    f"   - 作者：{row['authors']}",
                    f"   - 来源：{row['venue']}",
                    f"   - DOI/URL：{row['doi']} / {row['url']}",
                    f"   - 相关性：{row['relevance_reason_cn']}",
                    f"   - 对本课题启发：{row['possible_inspiration_for_my_project_cn']}",
                    "",
                ]
            )
    path.write_text("\n".join(lines), encoding="utf-8")


def select_reading_list(
    papers_path: Path = DATA_PROCESSED / "papers_master.csv",
    top_cited_path: Path = DATA_PROCESSED / "top_cited_papers.csv",
    processed_dir: Path = DATA_PROCESSED,
    reports_dir: Path = REPORTS,
    queries_path: Path = QUERIES_PATH,
    per_direction: int = 10,
) -> dict[str, Path]:
    if top_cited_path.is_dir():
        legacy_processed_dir = top_cited_path
        legacy_reports_dir = processed_dir
        processed_dir = legacy_processed_dir
        reports_dir = legacy_reports_dir
        top_cited_path = processed_dir / "top_cited_papers.csv"
    papers = prepare_papers(read_csv(papers_path))
    top_cited = read_csv(top_cited_path)
    if not top_cited.empty:
        top_titles = set(top_cited.get("title", pd.Series(dtype=str)).map(clean_text))
        papers["is_top_cited"] = papers["title"].map(lambda title: clean_text(title) in top_titles)
    else:
        papers["is_top_cited"] = False
    expanded = expand_by_direction(papers)
    selected_frames = []
    for direction, group in expanded.groupby("direction") if not expanded.empty else []:
        selected_frames.append(select_for_direction(group, per_direction=per_direction))
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    selected_rows = build_output_rows(selected)
    selected_frame = pd.DataFrame(selected_rows, columns=OUTPUT_COLUMNS)
    csv_path = processed_dir / "reading_list_by_direction.csv"
    report_path = reports_dir / "reading_list_by_direction.md"
    legacy_csv = processed_dir / "reading_list.csv"
    legacy_report = reports_dir / "reading_list.md"
    write_csv(csv_path, selected_frame)
    write_csv(legacy_csv, selected_frame)
    direction_names = load_direction_names(queries_path)
    write_report(report_path, selected_frame, direction_names)
    legacy_report.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")
    return {"csv": csv_path, "report": report_path, "legacy_csv": legacy_csv, "legacy_report": legacy_report}


def main() -> int:
    parser = argparse.ArgumentParser(description="Select a direction-by-direction reading list.")
    parser.add_argument("--per-direction", type=int, default=10)
    args = parser.parse_args()
    select_reading_list(per_direction=args.per_direction)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
