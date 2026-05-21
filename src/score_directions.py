from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_PROCESSED, QUERIES_PATH, REPORTS, UNCLEAR, clean_text, load_yaml, read_csv, safe_int, write_csv


SCORE_COLUMNS = [
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
    "data_evidence_cn",
]

STATIC_RULES = {
    "A": {
        "experimental_feasibility": 3.5,
        "equipment_accessibility": 2.5,
        "concrete_relevance": 3.5,
        "risk": "需要超重力/旋转填充床或等效强化碳化设备，且钢渣成分波动会影响可重复性。",
        "novelty_hint": 4.0,
    },
    "B": {
        "experimental_feasibility": 3.0,
        "equipment_accessibility": 2.5,
        "concrete_relevance": 5.0,
        "risk": "离心成型设备、模具和安全控制门槛较高，实验尺度放大不容易。",
        "novelty_hint": 3.0,
    },
    "C": {
        "experimental_feasibility": 2.0,
        "equipment_accessibility": 1.5,
        "concrete_relevance": 4.0,
        "risk": "微重力/超重力水化实验设备可获得性弱，普通材料实验室难以稳定复现重力场条件。",
        "novelty_hint": 4.5,
    },
    "D": {
        "experimental_feasibility": 4.5,
        "equipment_accessibility": 4.0,
        "concrete_relevance": 5.0,
        "risk": "方向较成熟，单纯重复 CO2 养护容易缺少新意，需要与材料体系或强化过程结合。",
        "novelty_hint": 2.5,
    },
    "E": {
        "experimental_feasibility": 4.0,
        "equipment_accessibility": 4.0,
        "concrete_relevance": 4.5,
        "risk": "固废来源和预碳化条件会显著影响活性，需建立清楚的材料表征和性能评价链条。",
        "novelty_hint": 4.0,
    },
    "F": {
        "experimental_feasibility": 2.5,
        "equipment_accessibility": 2.0,
        "concrete_relevance": 2.5,
        "risk": "传质强化文献多来自化工过程，和水泥/混凝土的直接耦合需要重新设计验证场景。",
        "novelty_hint": 4.0,
    },
}


def empty_metric() -> dict[str, Any]:
    return {
        "paper_count": 0,
        "recent_count": 0,
        "previous_count": 0,
        "growth": 0,
        "venue_count": 0,
        "mean_citation": 0.0,
        "reading_count": 0,
    }


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


def prepare_papers(papers: pd.DataFrame) -> pd.DataFrame:
    frame = papers.copy()
    if "citation_count" not in frame.columns and "cited_by_count" in frame.columns:
        frame["citation_count"] = frame["cited_by_count"]
    if "direction" not in frame.columns and "direction_labels" in frame.columns:
        frame["direction"] = frame["direction_labels"]
    for column in ["direction", "year", "citation_count", "venue", "title", "abstract", "query"]:
        if column not in frame.columns:
            frame[column] = UNCLEAR
    frame["year_num"] = frame["year"].map(safe_int)
    frame["citation_num"] = frame["citation_count"].map(lambda value: safe_int(value) or 0)
    return frame


def expand_by_direction(papers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in papers.iterrows():
        for direction in split_directions(row.get("direction")):
            item = row.to_dict()
            item["direction"] = direction
            rows.append(item)
    return pd.DataFrame(rows)


def scale(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return round(min(5.0, max(0.0, 5.0 * value / max_value)), 2)


def clamp_score(value: float) -> float:
    return round(min(5.0, max(0.0, value)), 2)


def direction_metrics(expanded: pd.DataFrame) -> dict[str, dict[str, Any]]:
    metrics = {}
    if expanded.empty:
        return metrics
    for direction, group in expanded.groupby("direction"):
        recent = group[(group["year_num"].fillna(0) >= 2022) & (group["year_num"].fillna(0) <= 2026)]
        previous = group[(group["year_num"].fillna(0) >= 2017) & (group["year_num"].fillna(0) <= 2021)]
        venues = group["venue"].map(clean_text)
        venues = venues[venues != UNCLEAR]
        citations = group["citation_num"].fillna(0)
        metrics[direction] = {
            "paper_count": int(len(group)),
            "recent_count": int(len(recent)),
            "previous_count": int(len(previous)),
            "growth": int(len(recent) - len(previous)),
            "venue_count": int(venues.nunique()),
            "mean_citation": round(float(citations.mean()), 2) if len(citations) else 0.0,
            "reading_count": 0,
        }
    return metrics


def add_reading_metrics(metrics: dict[str, dict[str, Any]], reading_list: pd.DataFrame) -> None:
    if reading_list.empty or "direction" not in reading_list.columns:
        return
    for _, row in reading_list.iterrows():
        for direction in split_directions(row.get("direction")):
            metrics.setdefault(direction, empty_metric())["reading_count"] += 1


def score_one(direction: str, metric: dict[str, Any], names: dict[str, str]) -> dict[str, Any]:
    metric = {**empty_metric(), **metric}
    max_reference = metric.get("_max_reference", {})
    heat = clamp_score(0.65 * scale(metric["recent_count"], max_reference["recent_count"]) + 0.35 * scale(max(metric["growth"], 0), max(max_reference["growth"], 1)))
    maturity = clamp_score(
        0.45 * scale(metric["paper_count"], max_reference["paper_count"])
        + 0.30 * scale(metric["venue_count"], max_reference["venue_count"])
        + 0.25 * scale(metric["mean_citation"], max_reference["mean_citation"])
    )
    rules = STATIC_RULES.get(direction, {})
    saturation_penalty = 0.8 if maturity >= 4.2 and metric["paper_count"] > 350 else 0.0
    novelty_space = clamp_score(float(rules.get("novelty_hint", 3.0)) + 0.25 * max(metric["growth"], 0) / max(max_reference["growth"], 1) - saturation_penalty)
    experimental = float(rules.get("experimental_feasibility", 3.0))
    equipment = float(rules.get("equipment_accessibility", 3.0))
    relevance = float(rules.get("concrete_relevance", 3.0))
    reading_signal = scale(metric.get("reading_count", 0), max_reference.get("reading_count", 1))
    publication = clamp_score(0.25 * heat + 0.18 * maturity + 0.22 * novelty_space + 0.25 * relevance + 0.10 * reading_signal)
    overall = clamp_score(
        0.17 * heat
        + 0.13 * maturity
        + 0.17 * novelty_space
        + 0.14 * experimental
        + 0.12 * equipment
        + 0.15 * relevance
        + 0.12 * publication
    )
    return {
        "direction": direction,
        "direction_zh": names.get(direction, direction),
        "overall_score": overall,
        "literature_heat": heat,
        "maturity": maturity,
        "novelty_space": novelty_space,
        "experimental_feasibility": experimental,
        "equipment_accessibility": equipment,
        "concrete_relevance": relevance,
        "publication_potential": publication,
        "recommendation_group": "unclear",
        "main_risk_cn": str(rules.get("risk", "主要风险需要结合具体实验条件人工判断。")),
        "score_explanation_cn": explanation(direction, heat, maturity, novelty_space, experimental, equipment, relevance, publication),
        "data_evidence_cn": f"论文总数={metric['paper_count']}；2022-2026近五年={metric['recent_count']}；2017-2021={metric['previous_count']}；增长={metric['growth']}；期刊/会议数={metric['venue_count']}；平均引用={metric['mean_citation']}；阅读清单={metric.get('reading_count', 0)}。",
    }


def explanation(direction: str, heat: float, maturity: float, novelty: float, experimental: float, equipment: float, relevance: float, publication: float) -> str:
    return (
        f"方向 {direction} 的评分由数据和可实施性共同决定：文献热度 {heat}/5，成熟度 {maturity}/5，"
        f"创新空间 {novelty}/5，实验可行性 {experimental}/5，设备可获得性 {equipment}/5，"
        f"混凝土相关性 {relevance}/5，发表潜力 {publication}/5。"
    )


def assign_recommendation_groups(scores: pd.DataFrame) -> pd.DataFrame:
    if scores.empty:
        return scores
    ranked = scores.sort_values("overall_score", ascending=False).reset_index(drop=True)
    groups = []
    for index, row in ranked.iterrows():
        if index < 2 and row["overall_score"] >= 3.6:
            groups.append("主攻方向")
        elif index < 4 and row["overall_score"] >= 3.0:
            groups.append("备用方向")
        else:
            groups.append("暂缓方向")
    ranked["recommendation_group"] = groups
    return ranked


def build_scores(papers: pd.DataFrame, reading_list: pd.DataFrame, names: dict[str, str]) -> pd.DataFrame:
    expanded = expand_by_direction(prepare_papers(papers))
    metrics = direction_metrics(expanded)
    add_reading_metrics(metrics, reading_list)
    for direction in names:
        metrics.setdefault(direction, empty_metric())
    if not metrics:
        return pd.DataFrame(columns=SCORE_COLUMNS)
    max_reference = {
        "paper_count": max(metric.get("paper_count", 0) for metric in metrics.values()) or 1,
        "recent_count": max(metric.get("recent_count", 0) for metric in metrics.values()) or 1,
        "growth": max(max(metric.get("growth", 0), 0) for metric in metrics.values()) or 1,
        "venue_count": max(metric.get("venue_count", 0) for metric in metrics.values()) or 1,
        "mean_citation": max(metric.get("mean_citation", 0) for metric in metrics.values()) or 1,
        "reading_count": max(metric.get("reading_count", 0) for metric in metrics.values()) or 1,
    }
    rows = []
    for direction in sorted(metrics):
        metric = dict(metrics[direction])
        metric["_max_reference"] = max_reference
        rows.append(score_one(direction, metric, names))
    return assign_recommendation_groups(pd.DataFrame(rows, columns=SCORE_COLUMNS))


def write_report(path: Path, scores: pd.DataFrame, landscape_text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 方向可行性评分报告",
        "",
        "评分满分 5 分，依据 `papers_master.csv`、`reading_list_by_direction.csv` 和 `landscape_summary.md` 的数据线索生成。分数是初筛工具，不替代人工选题判断。",
        "",
        "## 推荐排序",
        "",
    ]
    for group_name in ["主攻方向", "备用方向", "暂缓方向"]:
        subset = scores[scores["recommendation_group"] == group_name]
        lines.append(f"### {group_name}")
        if subset.empty:
            lines.append("- unclear")
        else:
            for _, row in subset.iterrows():
                lines.append(f"- {row['direction']} - {row['direction_zh']}：{row['overall_score']}/5")
        lines.append("")
    lines.append("## 分方向解释")
    lines.append("")
    for _, row in scores.iterrows():
        lines.extend(
            [
                f"### {row['direction']} - {row['direction_zh']}",
                "",
                f"- 总分：{row['overall_score']}/5；推荐类别：{row['recommendation_group']}。",
                f"- 分项：文献热度 {row['literature_heat']}，成熟度 {row['maturity']}，创新空间 {row['novelty_space']}，实验可行性 {row['experimental_feasibility']}，设备可获得性 {row['equipment_accessibility']}，混凝土相关性 {row['concrete_relevance']}，发表潜力 {row['publication_potential']}。",
                f"- 评分解释：{row['score_explanation_cn']}",
                f"- 数据依据：{row['data_evidence_cn']}",
                f"- 主要风险：{row['main_risk_cn']}",
                "",
            ]
        )
    lines.extend(
        [
            "## 说明",
            "",
            "- literature_heat 主要由 2022-2026 论文数和相对 2017-2021 的增长估算。",
            "- maturity 由论文总量、来源期刊/会议数量和平均引用估算。",
            "- novelty_space 结合方向规则和成熟度惩罚估算，成熟但拥挤的方向会降低创新空间。",
            "- experimental_feasibility、equipment_accessibility、concrete_relevance 使用透明方向规则，适合普通材料实验室的方向分数更高。",
            f"- landscape_summary.md 可用长度：{len(landscape_text)} 字符，用作人工复核背景，不从中抽取未在 CSV 中出现的论文。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def score_directions(
    processed_dir: Path = DATA_PROCESSED,
    reports_dir: Path = REPORTS,
    queries_path: Path = QUERIES_PATH,
    papers_path: Path | None = None,
    reading_list_path: Path | None = None,
    landscape_report_path: Path | None = None,
) -> dict[str, Path]:
    if papers_path is None:
        papers_path = processed_dir / "papers_master.csv"
        if not papers_path.exists():
            papers_path = processed_dir / "works_master.csv"
    if reading_list_path is None:
        reading_list_path = processed_dir / "reading_list_by_direction.csv"
        if not reading_list_path.exists():
            reading_list_path = processed_dir / "reading_list.csv"
    landscape_report_path = landscape_report_path or reports_dir / "landscape_summary.md"
    papers = read_csv(papers_path)
    reading_list = read_csv(reading_list_path)
    landscape_text = landscape_report_path.read_text(encoding="utf-8") if landscape_report_path.exists() else ""
    names = load_direction_names(queries_path)
    scores = build_scores(papers, reading_list, names)
    csv_path = processed_dir / "direction_score.csv"
    legacy_csv_path = processed_dir / "direction_scores.csv"
    report_path = reports_dir / "direction_score_report.md"
    legacy_report_path = reports_dir / "direction_scores.md"
    write_csv(csv_path, scores)
    write_csv(legacy_csv_path, scores)
    write_report(report_path, scores, landscape_text)
    legacy_report_path.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")
    return {"csv": csv_path, "report": report_path, "legacy_csv": legacy_csv_path, "legacy_report": legacy_report_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Score the six research directions on a 5-point feasibility scale.")
    parser.parse_args()
    score_directions()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
