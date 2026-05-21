from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from common import DATA_PROCESSED, FIGURES, QUERIES_PATH, REPORTS, UNCLEAR, clean_text, ensure_dirs, load_yaml, read_csv, safe_int, write_csv
from merge_and_clean import clean_records, sample_records

START_YEAR = 2015
END_YEAR = 2026


def load_direction_meta(queries_path: Path = QUERIES_PATH) -> dict[str, dict[str, str]]:
    if not queries_path.exists():
        return {}
    data = load_yaml(queries_path)
    meta: dict[str, dict[str, str]] = {}
    for direction in data.get("directions", []) or []:
        if not isinstance(direction, dict):
            continue
        direction_id = str(direction.get("id", "")).strip()
        if not direction_id:
            continue
        meta[direction_id] = {
            "zh": str(direction.get("zh") or direction.get("name") or direction_id),
            "name_en": str(direction.get("name_en") or direction_id),
            "note_zh": str(direction.get("note_zh") or "unclear"),
        }
    return meta


def split_labels(value: Any) -> list[str]:
    text = clean_text(value)
    if text == UNCLEAR:
        return [UNCLEAR]
    labels = [item.strip() for item in text.split("|") if item.strip()]
    return labels or [UNCLEAR]


def prepare_works(works: pd.DataFrame) -> pd.DataFrame:
    if works.empty:
        return works
    frame = works.copy()
    if "citation_count" not in frame.columns and "cited_by_count" in frame.columns:
        frame["citation_count"] = frame["cited_by_count"]
    if "direction" not in frame.columns and "direction_labels" in frame.columns:
        frame["direction"] = frame["direction_labels"]
    if "query" not in frame.columns and "matched_query" in frame.columns:
        frame["query"] = frame["matched_query"]
    for column in ["title", "year", "authors", "venue", "doi", "url", "abstract", "citation_count", "direction", "query", "source_database"]:
        if column not in frame.columns:
            frame[column] = UNCLEAR
    frame["year_num"] = frame["year"].map(safe_int)
    frame["citation_num"] = frame["citation_count"].map(lambda value: safe_int(value) or 0)
    frame["title"] = frame["title"].map(clean_text)
    frame["venue"] = frame["venue"].map(clean_text)
    frame["authors"] = frame["authors"].map(clean_text)
    return frame


def expand_by_direction(works: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if works.empty:
        return pd.DataFrame()
    for _, row in works.iterrows():
        for direction in split_labels(row.get("direction")):
            item = row.to_dict()
            item["direction"] = direction
            rows.append(item)
    return pd.DataFrame(rows)


def analyze_works(
    works_path: Path = DATA_PROCESSED / "papers_master.csv",
    processed_dir: Path = DATA_PROCESSED,
    reports_dir: Path = REPORTS,
    figures_dir: Path = FIGURES,
    queries_path: Path = QUERIES_PATH,
) -> dict[str, Path]:
    ensure_dirs()
    processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    works = prepare_works(read_csv(works_path))
    expanded = expand_by_direction(works)
    direction_meta = load_direction_meta(queries_path)

    direction_summary = make_direction_summary(expanded, direction_meta)
    trend = make_year_trend(expanded)
    top_venues = make_top_venues(expanded)
    top_authors = make_top_authors(expanded)
    top_cited = make_top_cited_by_direction(expanded)

    outputs = {
        "summary_report": reports_dir / "landscape_summary.md",
        "direction_count_figure": figures_dir / "direction_paper_count.png",
        "year_trend_figure": figures_dir / "year_trend_by_direction.png",
        "top_venues_figure": figures_dir / "top_venues_by_direction.png",
        "top_cited": processed_dir / "top_cited_papers.csv",
        "direction_summary": processed_dir / "direction_summary.csv",
        "yearly_counts": processed_dir / "yearly_counts.csv",
        "venues": processed_dir / "venue_summary.csv",
        "authors": processed_dir / "author_summary.csv",
        "legacy_report": reports_dir / "landscape_report.md",
        "legacy_trend_figure": figures_dir / "yearly_trend.png",
        "legacy_venue_figure": figures_dir / "top_venues.png",
        "report": reports_dir / "landscape_summary.md",
        "trend_figure": figures_dir / "year_trend_by_direction.png",
        "venue_figure": figures_dir / "top_venues_by_direction.png",
    }

    write_csv(outputs["direction_summary"], direction_summary)
    write_csv(outputs["yearly_counts"], trend)
    write_csv(outputs["venues"], top_venues)
    write_csv(outputs["authors"], top_authors)
    write_csv(outputs["top_cited"], top_cited)
    write_report(outputs["summary_report"], direction_summary, trend, top_venues, top_authors, top_cited, direction_meta)
    outputs["legacy_report"].write_text(outputs["summary_report"].read_text(encoding="utf-8"), encoding="utf-8")
    plot_direction_counts(direction_summary, outputs["direction_count_figure"])
    plot_year_trend(trend, outputs["year_trend_figure"])
    plot_top_venues(top_venues, outputs["top_venues_figure"])
    plot_year_trend(trend, outputs["legacy_trend_figure"])
    plot_top_venues(top_venues, outputs["legacy_venue_figure"])
    print(f"wrote {outputs['summary_report']}")
    print(f"wrote {outputs['top_cited']}")
    return outputs


def make_direction_summary(expanded: pd.DataFrame, direction_meta: dict[str, dict[str, str]]) -> pd.DataFrame:
    columns = [
        "direction",
        "direction_zh",
        "paper_count",
        "trend_2015_2026",
        "recent_count_2022_2026",
        "recent_count",
        "mean_citations",
        "active_judgement",
        "relation_note",
    ]
    if expanded.empty:
        return pd.DataFrame(columns=columns)
    rows = []
    directions = sorted(set(expanded["direction"].dropna().astype(str)))
    for direction in directions:
        group = expanded[expanded["direction"] == direction]
        trend_counts = count_years(group)
        recent_count = sum(trend_counts.get(year, 0) for year in range(2022, END_YEAR + 1))
        total_2015_2026 = sum(trend_counts.values())
        citation_values = [safe_int(value) for value in group["citation_count"]]
        citation_values = [value for value in citation_values if value is not None]
        rows.append(
            {
                "direction": direction,
                "direction_zh": direction_meta.get(direction, {}).get("zh", direction),
                "paper_count": len(group),
                "trend_2015_2026": "; ".join(f"{year}:{trend_counts.get(year, 0)}" for year in range(START_YEAR, END_YEAR + 1)),
                "recent_count_2022_2026": recent_count,
                "recent_count": recent_count,
                "mean_citations": round(sum(citation_values) / len(citation_values), 2) if citation_values else UNCLEAR,
                "active_judgement": active_judgement(total_2015_2026, recent_count),
                "relation_note": direction_meta.get(direction, {}).get("note_zh", "unclear"),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def count_years(group: pd.DataFrame) -> dict[int, int]:
    counts = {year: 0 for year in range(START_YEAR, END_YEAR + 1)}
    for year in group["year_num"].dropna().astype(int):
        if START_YEAR <= year <= END_YEAR:
            counts[int(year)] += 1
    return counts


def active_judgement(total_2015_2026: int, recent_count: int) -> str:
    if recent_count >= 20 or (total_2015_2026 >= 30 and recent_count >= 8):
        return "活跃"
    if recent_count >= 5:
        return "有一定活跃度"
    if total_2015_2026 > 0:
        return "相对小众或活跃度有限"
    return "unclear"


def make_year_trend(expanded: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if expanded.empty:
        return pd.DataFrame(columns=["direction", "year", "paper_count"])
    for direction in sorted(set(expanded["direction"].dropna().astype(str))):
        group = expanded[expanded["direction"] == direction]
        counts = count_years(group)
        for year in range(START_YEAR, END_YEAR + 1):
            rows.append({"direction": direction, "year": year, "paper_count": counts[year]})
    return pd.DataFrame(rows)


def make_top_venues(expanded: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if expanded.empty:
        return pd.DataFrame(columns=["direction", "venue", "paper_count", "total_citations"])
    rows = []
    valid = expanded[expanded["venue"].map(lambda value: clean_text(value) != UNCLEAR)].copy()
    for (direction, venue), group in valid.groupby(["direction", "venue"]):
        rows.append(
            {
                "direction": direction,
                "venue": venue,
                "paper_count": len(group),
                "total_citations": int(group["citation_num"].sum()),
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=["direction", "venue", "paper_count", "total_citations"])
    return frame.sort_values(["direction", "paper_count", "total_citations"], ascending=[True, False, False]).groupby("direction").head(top_n)


def make_top_authors(expanded: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    if expanded.empty:
        return pd.DataFrame(columns=["direction", "author", "paper_count", "total_citations"])
    for _, row in expanded.iterrows():
        authors = [author.strip() for author in str(row.get("authors", "")).split(";") if author.strip() and author.strip().lower() != UNCLEAR]
        for author in authors:
            key = (row["direction"], author)
            item = rows.setdefault(key, {"direction": row["direction"], "author": author, "paper_count": 0, "total_citations": 0})
            item["paper_count"] += 1
            item["total_citations"] += safe_int(row.get("citation_count")) or 0
    frame = pd.DataFrame(rows.values())
    if frame.empty:
        return pd.DataFrame(columns=["direction", "author", "paper_count", "total_citations"])
    return frame.sort_values(["direction", "paper_count", "total_citations"], ascending=[True, False, False]).groupby("direction").head(top_n)


def make_top_cited_by_direction(expanded: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    columns = ["direction", "rank", "title", "year", "authors", "venue", "doi", "url", "citation_count", "source_database", "query"]
    if expanded.empty:
        return pd.DataFrame(columns=columns)
    rows = []
    for direction, group in expanded.groupby("direction"):
        top = group.sort_values("citation_num", ascending=False).head(top_n)
        for rank, (_, row) in enumerate(top.iterrows(), start=1):
            rows.append(
                {
                    "direction": direction,
                    "rank": rank,
                    "title": row.get("title", UNCLEAR),
                    "year": row.get("year", UNCLEAR),
                    "authors": row.get("authors", UNCLEAR),
                    "venue": row.get("venue", UNCLEAR),
                    "doi": row.get("doi", UNCLEAR),
                    "url": row.get("url", UNCLEAR),
                    "citation_count": row.get("citation_count", UNCLEAR),
                    "source_database": row.get("source_database", UNCLEAR),
                    "query": row.get("query", UNCLEAR),
                }
            )
    return pd.DataFrame(rows, columns=columns)


def write_report(
    path: Path,
    direction_summary: pd.DataFrame,
    trend: pd.DataFrame,
    top_venues: pd.DataFrame,
    top_authors: pd.DataFrame,
    top_cited: pd.DataFrame,
    direction_meta: dict[str, dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 文献景观总结",
        "",
        "本报告基于 `data/processed/papers_master.csv` 自动聚合生成；缺失信息保留为 `unclear`，不补造论文或结论。",
        "",
    ]
    if direction_summary.empty:
        lines.append("unclear: 未读取到可分析记录。")
    for _, summary in direction_summary.iterrows():
        direction = summary["direction"]
        zh = summary["direction_zh"]
        lines.extend(
            [
                f"## {direction} - {zh}",
                "",
                f"- 论文总数：{summary['paper_count']}。",
                f"- 2015-2026 年发文趋势：{summary['trend_2015_2026']}。",
                f"- 代表期刊/会议：{format_top_items(top_venues[top_venues['direction'] == direction], 'venue')}。",
                f"- 代表作者：{format_top_items(top_authors[top_authors['direction'] == direction], 'author')}。",
                f"- 高被引论文：{format_top_papers(top_cited[top_cited['direction'] == direction])}。",
                f"- 初步判断：{summary['active_judgement']}。依据是 2015-2026 总量和 2022-2026 近年数量。",
                f"- 与“超重力-混凝土”课题的关系：{clean_text(direction_meta.get(direction, {}).get('note_zh', summary.get('relation_note', 'unclear'))).rstrip('。.')}。",
                "",
            ]
        )
    lines.extend(
        [
            "## 数据依据",
            "",
            "- 主表：`data/processed/papers_master.csv`",
            "- 高被引表：`data/processed/top_cited_papers.csv`",
            "- 趋势统计：`data/processed/yearly_counts.csv`",
            "- 期刊统计：`data/processed/venue_summary.csv`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_top_items(frame: pd.DataFrame, column: str) -> str:
    if frame.empty:
        return "unclear"
    items = []
    for _, row in frame.head(3).iterrows():
        items.append(f"{row[column]}（{row['paper_count']} 篇）")
    return "；".join(items)


def format_top_papers(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "unclear"
    items = []
    for _, row in frame.head(3).iterrows():
        items.append(f"{row['title']}（{row['year']}，引用 {row['citation_count']}）")
    return "；".join(items)


def empty_plot(path: Path, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, "unclear: no data", ha="center", va="center")
    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_direction_counts(direction_summary: pd.DataFrame, path: Path) -> None:
    if direction_summary.empty:
        empty_plot(path, "Paper Count by Direction")
        return
    frame = direction_summary.sort_values("paper_count", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(frame["direction"], frame["paper_count"], color="#4c78a8")
    ax.set_title("Paper Count by Direction")
    ax.set_xlabel("Direction")
    ax.set_ylabel("Paper Count")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_year_trend(trend: pd.DataFrame, path: Path) -> None:
    if trend.empty:
        empty_plot(path, "Year Trend by Direction")
        return
    fig, ax = plt.subplots(figsize=(11, 6))
    for direction, group in trend.groupby("direction"):
        ax.plot(group["year"], group["paper_count"], marker="o", linewidth=1.6, label=direction)
    ax.set_title("Year Trend by Direction")
    ax.set_xlabel("Year")
    ax.set_ylabel("Paper Count")
    ax.set_xticks(list(range(START_YEAR, END_YEAR + 1)))
    ax.legend(title="Direction")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_top_venues(top_venues: pd.DataFrame, path: Path) -> None:
    if top_venues.empty:
        empty_plot(path, "Top Venues by Direction")
        return
    frame = top_venues.copy()
    frame["label"] = frame["direction"] + " | " + frame["venue"].astype(str).str.slice(0, 42)
    frame = frame.sort_values(["direction", "paper_count"], ascending=[True, True]).tail(24)
    fig, ax = plt.subplots(figsize=(12, max(6, 0.35 * len(frame))))
    ax.barh(frame["label"], frame["paper_count"], color="#59a14f")
    ax.set_title("Top Venues by Direction")
    ax.set_xlabel("Paper Count")
    ax.set_ylabel("Direction | Venue")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze the cleaned literature landscape from papers_master.csv.")
    parser.add_argument("--sample", action="store_true", help="Create sample papers before analysis.")
    args = parser.parse_args()
    if args.sample:
        cleaned, _stats = clean_records(sample_records())
        write_csv(DATA_PROCESSED / "papers_master.csv", cleaned)
        write_csv(DATA_PROCESSED / "works_master.csv", cleaned)
    analyze_works()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
