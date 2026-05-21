from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_PROCESSED, REPORTS, UNCLEAR, clean_text, read_csv, safe_int


TITLE = "超重力与混凝土结合方向的文献侦察与选题可行性分析"

INPUT_FILES = {
    "papers": "papers_master.csv",
    "top_cited": "top_cited_papers.csv",
    "reading": "reading_list_by_direction.csv",
    "scores": "direction_score.csv",
    "landscape": "landscape_summary.md",
    "reading_report": "reading_list_by_direction.md",
    "score_report": "direction_score_report.md",
}

DIRECTION_NAMES = {
    "A": "超重力碳化固废",
    "B": "离心/超重力成型混凝土",
    "C": "重力场对水泥水化影响",
    "D": "CO2养护与碳化混凝土",
    "E": "碳化固废辅助胶凝材料",
    "F": "旋转填充床与传质强化",
}

NOISE_NOTES = {
    "B": "该方向部分高被引题录偏向离心制造、复合材料或数值方法，需人工复核其与混凝土离心成型的直接相关性。",
    "C": "该方向可能混入 3D 打印、水化泛化或微重力相邻主题，需人工补充检索水泥浆体在重力场中的专门实验文献。",
    "F": "该方向化工传质强化文献较多，和水泥/混凝土体系的直接耦合证据不足，需人工复核应用场景。",
}

GAP_HINTS = {
    "A": [
        "超重力或旋转填充床条件下固废碳化产物与胶凝活性之间的定量关系仍需收敛。",
        "钢渣/转炉渣组成波动较大，需要把材料表征、碳化效率和砂浆性能放在同一评价链条中。",
        "高重力强化过程与后续混凝土应用之间仍缺少低成本、小试可复现方案。",
    ],
    "B": [
        "离心成型研究与材料微结构、耐久性、低碳胶凝体系之间的交叉仍需人工补充检索。",
        "现有题录中存在相邻制造主题噪声，代表论文需人工筛掉非混凝土研究。",
        "实验从试样到管桩或构件尺度的放大关系仍是主要不确定点。",
    ],
    "C": [
        "水泥水化受微重力/超重力影响的专门数据较少，需补充针对 cement paste 的精确检索。",
        "重力场变量、孔结构演化和力学性能之间的机制链条仍不清晰。",
        "普通材料实验室难以稳定复现重力场条件，因此短期可做性受限。",
    ],
    "D": [
        "CO2 养护方向已较成熟，单独重复强度或吸碳率测试创新性不足。",
        "更有价值的空白在于把 CO2 养护与固废 SCM、预碳化粉体或强化传质过程耦合。",
        "需要同时报告碳吸收、早期性能、长期耐久性和环境收益，避免单指标结论。",
    ],
    "E": [
        "碳化固废作为 SCM 的活性来源、反应程度和水化贡献仍需更清晰地区分。",
        "废混凝土粉、钢渣、再生细粉等原料差异会影响可重复性，需要建立材料分级策略。",
        "预碳化制度与替代率、强度、耐久性之间的窗口仍有系统优化空间。",
    ],
    "F": [
        "旋转填充床和传质强化研究多在化工体系中展开，直接迁移到水泥/混凝土需要新的反应器和浆体适配验证。",
        "矿化碳化效率与后续胶凝性能之间的关联证据不足。",
        "设备门槛较高，短期更适合作为 A/E/D 的过程强化变量，而非独立主线。",
    ],
}

TITLE_HINTS = {
    "A": [
        "超重力强化钢渣碳化及其作为低碳胶凝材料的性能评价",
        "旋转填充床条件下转炉渣 CO2 矿化与砂浆性能耦合机制",
        "高重力碳化固废的反应程度、微结构和胶凝活性关系研究",
    ],
    "B": [
        "离心成型对低碳胶凝混凝土密实度和耐久性的影响",
        "管桩混凝土离心过程中的浆体迁移与界面结构演化",
        "含碳化固废胶凝材料的离心成型混凝土性能初探",
    ],
    "C": [
        "重力场变化对水泥浆体早期水化和孔结构形成的影响",
        "超重力条件下水泥基材料水化动力学与微结构演化",
        "微重力/超重力水泥浆体实验数据的系统复核与小试设计",
    ],
    "D": [
        "CO2 养护下含碳化固废 SCM 砂浆的早期性能与固碳效率",
        "加速碳化养护对低熟料胶凝体系强度和耐久性的影响",
        "CO2 养护与预碳化再生粉体协同提升水泥基材料性能研究",
    ],
    "E": [
        "碳化废混凝土粉作为辅助胶凝材料的活性评价与替代率优化",
        "碳化钢渣 SCM 对水泥水化、孔结构和力学性能的影响",
        "不同固废预碳化制度对低碳砂浆性能的调控机制",
    ],
    "F": [
        "旋转填充床强化矿化碳化过程及其水泥基材料应用边界",
        "传质强化条件下钙基固废 CO2 矿化效率与胶凝性能关联",
        "面向低碳胶凝材料的高重力碳化反应器小试方案研究",
    ],
}


def direction_order() -> list[str]:
    return ["A", "B", "C", "D", "E", "F"]


def split_direction(value: Any) -> list[str]:
    text = clean_text(value)
    if text == UNCLEAR:
        return []
    return [item.strip() for item in re.split(r"[|,;]", text) if item.strip()]


def load_inputs(processed_dir: Path = DATA_PROCESSED, reports_dir: Path = REPORTS) -> dict[str, Any]:
    data: dict[str, Any] = {"missing": []}
    for key, filename in INPUT_FILES.items():
        base = processed_dir if key in {"papers", "top_cited", "reading", "scores"} else reports_dir
        path = base / filename
        data[f"{key}_path"] = path
        if key in {"papers", "top_cited", "reading", "scores"}:
            data[key] = read_csv(path)
        else:
            data[key] = path.read_text(encoding="utf-8") if path.exists() else ""
        if not path.exists():
            data["missing"].append(path)
    return data


def expanded_papers(papers: pd.DataFrame) -> pd.DataFrame:
    if papers.empty or "direction" not in papers.columns:
        return pd.DataFrame()
    rows = []
    for _, row in papers.iterrows():
        for direction in split_direction(row.get("direction")):
            item = row.to_dict()
            item["direction"] = direction
            rows.append(item)
    return pd.DataFrame(rows)


def numeric(value: Any, default: float = 0.0) -> float:
    if clean_text(value) == UNCLEAR:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score_label(value: Any) -> str:
    score = numeric(value)
    if score >= 4.2:
        return f"高（{score:g}/5）"
    if score >= 3.2:
        return f"中高（{score:g}/5）"
    if score > 0:
        return f"中低（{score:g}/5）"
    return "数据不足，需人工补充检索"


def difficulty_label(feasibility: Any) -> str:
    score = numeric(feasibility)
    if score >= 4.0:
        return f"低（可行性 {score:g}/5）"
    if score >= 3.0:
        return f"中（可行性 {score:g}/5）"
    if score > 0:
        return f"高（可行性 {score:g}/5）"
    return "数据不足，需人工补充检索"


def equipment_label(accessibility: Any) -> str:
    score = numeric(accessibility)
    if score >= 4.0:
        return f"低（设备可获得性 {score:g}/5）"
    if score >= 3.0:
        return f"中（设备可获得性 {score:g}/5）"
    if score > 0:
        return f"高（设备可获得性 {score:g}/5）"
    return "数据不足，需人工补充检索"


def direction_metrics(papers: pd.DataFrame, scores: pd.DataFrame) -> dict[str, dict[str, Any]]:
    expanded = expanded_papers(papers)
    metrics: dict[str, dict[str, Any]] = {}
    for direction in direction_order():
        score_row = scores[scores.get("direction", pd.Series(dtype=str)).astype(str) == direction]
        score = score_row.iloc[0].to_dict() if not score_row.empty else {}
        subset = expanded[expanded["direction"] == direction] if not expanded.empty else pd.DataFrame()
        years = subset["year"].map(safe_int) if "year" in subset.columns and not subset.empty else pd.Series(dtype=object)
        recent_count = int(((years >= 2022) & (years <= 2026)).sum()) if len(years) else 0
        venues = subset["venue"].map(clean_text) if "venue" in subset.columns and not subset.empty else pd.Series(dtype=str)
        venues = venues[venues != UNCLEAR]
        metrics[direction] = {
            "direction": direction,
            "direction_zh": clean_text(score.get("direction_zh")) if score else DIRECTION_NAMES[direction],
            "paper_count": int(len(subset)),
            "recent_count": recent_count,
            "top_venues": "; ".join(venues.value_counts().head(3).index.tolist()) if len(venues) else UNCLEAR,
            "overall_score": score.get("overall_score", UNCLEAR),
            "literature_heat": score.get("literature_heat", UNCLEAR),
            "novelty_space": score.get("novelty_space", UNCLEAR),
            "experimental_feasibility": score.get("experimental_feasibility", UNCLEAR),
            "equipment_accessibility": score.get("equipment_accessibility", UNCLEAR),
            "concrete_relevance": score.get("concrete_relevance", UNCLEAR),
            "publication_potential": score.get("publication_potential", UNCLEAR),
            "recommendation_group": clean_text(score.get("recommendation_group")) if score else "数据不足，需人工补充检索",
            "main_risk_cn": clean_text(score.get("main_risk_cn")) if score else "数据不足，需人工补充检索",
            "data_evidence_cn": clean_text(score.get("data_evidence_cn")) if score else "数据不足，需人工补充检索",
        }
    return metrics


def record_key(row: pd.Series) -> str:
    doi = clean_text(row.get("doi"))
    if doi != UNCLEAR:
        return f"doi:{doi.lower()}"
    return f"title:{clean_text(row.get('title')).lower()}"


def select_by_direction(frame: pd.DataFrame, direction: str) -> pd.DataFrame:
    if frame.empty or "direction" not in frame.columns:
        return pd.DataFrame()
    mask = frame["direction"].astype(str).map(lambda value: direction in split_direction(value))
    return frame[mask].copy()


def representative_papers(reading: pd.DataFrame, top_cited: pd.DataFrame, direction: str, limit: int = 5) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for frame in [select_by_direction(reading, direction), select_by_direction(top_cited, direction)]:
        if frame.empty:
            continue
        if "citation_count" in frame.columns:
            frame = frame.assign(_citation=frame["citation_count"].map(lambda value: numeric(value, -1))).sort_values("_citation", ascending=False)
        for _, row in frame.iterrows():
            key = record_key(row)
            if key in seen:
                continue
            seen.add(key)
            selected.append(
                {
                    "title": clean_text(row.get("title")),
                    "year": clean_text(row.get("year")),
                    "authors": clean_text(row.get("authors")),
                    "venue": clean_text(row.get("venue")),
                    "doi": clean_text(row.get("doi")),
                    "url": clean_text(row.get("url")),
                    "citation_count": clean_text(row.get("citation_count")),
                }
            )
            if len(selected) >= limit:
                return selected
    return selected


def recommendation_lines(scores: pd.DataFrame, group_name: str) -> list[str]:
    if scores.empty or "recommendation_group" not in scores.columns:
        return ["- 数据不足，需人工补充检索。"]
    subset = scores[scores["recommendation_group"].astype(str) == group_name].copy()
    if subset.empty:
        return ["- 数据不足，需人工补充检索。"]
    subset["_score"] = subset["overall_score"].map(numeric)
    subset = subset.sort_values("_score", ascending=False)
    lines = []
    for _, row in subset.iterrows():
        direction = clean_text(row.get("direction"))
        zh = clean_text(row.get("direction_zh"))
        lines.append(f"- {direction} - {zh}：总分 {numeric(row.get('overall_score')):g}/5。主要依据：{clean_text(row.get('data_evidence_cn'))}")
    return lines


def format_paper_list(papers: list[dict[str, Any]]) -> list[str]:
    if not papers:
        return ["- 数据不足，需人工补充检索。"]
    lines = []
    for paper in papers:
        lines.append(
            "- "
            f"{paper['title']}（{paper['year']}，引用 {paper['citation_count']}；"
            f"作者：{paper['authors']}；来源：{paper['venue']}；DOI/URL：{paper['doi']} / {paper['url']}）"
        )
    return lines


def final_table(metrics: dict[str, dict[str, Any]]) -> list[str]:
    lines = [
        "| 方向 | 热度 | 创新性 | 实验难度 | 设备需求 | 推荐程度 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for direction in direction_order():
        item = metrics[direction]
        lines.append(
            "| "
            f"{direction} - {item['direction_zh']} | "
            f"{score_label(item['literature_heat'])} | "
            f"{score_label(item['novelty_space'])} | "
            f"{difficulty_label(item['experimental_feasibility'])} | "
            f"{equipment_label(item['equipment_accessibility'])} | "
            f"{item['recommendation_group']}（总分 {clean_text(item['overall_score'])}/5） |"
        )
    return lines


def data_gap_lines(missing: list[Path]) -> list[str]:
    if not missing:
        return ["- 本轮报告所需 7 个输入文件均已找到。"]
    lines = ["- 以下输入文件缺失，相关结论标注为“数据不足，需人工补充检索”："]
    for path in missing:
        lines.append(f"- {path}")
    return lines


def write_final_report(data: dict[str, Any], output_path: Path) -> Path:
    papers: pd.DataFrame = data["papers"]
    top_cited: pd.DataFrame = data["top_cited"]
    reading: pd.DataFrame = data["reading"]
    scores: pd.DataFrame = data["scores"]
    metrics = direction_metrics(papers, scores)
    source_counts = papers["source_database"].value_counts().to_dict() if not papers.empty and "source_database" in papers.columns else {}
    source_text = "；".join(f"{source} {count} 条" for source, count in source_counts.items()) if source_counts else "数据不足，需人工补充检索"

    lines: list[str] = [
        f"# {TITLE}",
        "",
        "本报告由项目中已经生成的 CSV 与 Markdown 文件自动汇总，不新增、猜测或补造论文题录。若某项输入缺失或字段为空，统一标注为“数据不足，需人工补充检索”或 `unclear`。",
        "",
        "## 数据完整性",
        "",
        *data_gap_lines(data["missing"]),
        "",
        "## 1. 研究背景",
        "",
        "超重力与混凝土结合的核心动机，是把强化传质、矿化碳化、固废资源化和低碳胶凝材料设计连接起来。现有数据中，D（CO2养护与碳化混凝土）和 E（碳化固废辅助胶凝材料）与水泥/砂浆/混凝土最直接；A（超重力碳化固废）提供过程强化入口；B、C、F 分别对应离心成型、重力场水化和旋转填充床传质强化，但短期实验条件与题录相关性需要进一步复核。",
        "",
        "## 2. 调研方法",
        "",
        f"- 数据来源：主表 `papers_master.csv` 当前来源计数为 {source_text}。既有流程以 OpenAlex 为主，Semantic Scholar 和 Crossref 用于补充或校验；本最终报告不重新联网检索。",
        "- 检索范围：A-F 六个方向的英文关键词和短语检索式，覆盖 high gravity carbonation、rotating packed bed、centrifuged concrete、microgravity cement paste、CO2 curing concrete、carbonated SCM 等表达。",
        "- 清洗筛选：原始结果经 DOI、OpenAlex/Semantic Scholar ID、标题-年份相似度去重；阅读清单优先 2018 年后、高引用和 2023 年后新论文。",
        "- 评分方法：热度、成熟度、创新空间、实验可行性、设备可获得性、混凝土相关性和发表潜力来自 `direction_score.csv`；代表论文优先来自 `reading_list_by_direction.csv`，不足时用 `top_cited_papers.csv` 补足。",
        "",
        "## 3. 六个方向总体对比",
        "",
        "| 方向 | 论文总数 | 2022-2026 论文数 | 总分 | 推荐类别 | 主要风险 |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for direction in direction_order():
        item = metrics[direction]
        lines.append(
            f"| {direction} - {item['direction_zh']} | {item['paper_count']} | {item['recent_count']} | "
            f"{clean_text(item['overall_score'])} | {item['recommendation_group']} | {item['main_risk_cn']} |"
        )

    lines.extend(["", "## 4. 每个方向的研究现状", ""])
    for direction in direction_order():
        item = metrics[direction]
        note = f" {NOISE_NOTES[direction]}" if direction in NOISE_NOTES else ""
        lines.append(
            f"### {direction} - {item['direction_zh']}\n"
            f"- 数据概况：论文总数 {item['paper_count']}，2022-2026 年论文数 {item['recent_count']}。{item['data_evidence_cn']}\n"
            f"- 代表期刊/会议：{item['top_venues']}。\n"
            f"- 评分状态：热度 {clean_text(item['literature_heat'])}/5，创新空间 {clean_text(item['novelty_space'])}/5，混凝土相关性 {clean_text(item['concrete_relevance'])}/5，推荐类别为 {item['recommendation_group']}。{note}"
        )
        lines.append("")

    lines.extend(["## 5. 每个方向的代表论文", ""])
    representative_cache: dict[str, list[dict[str, Any]]] = {}
    for direction in direction_order():
        item = metrics[direction]
        papers_for_direction = representative_papers(reading, top_cited, direction)
        representative_cache[direction] = papers_for_direction
        lines.append(f"### {direction} - {item['direction_zh']}")
        lines.extend(format_paper_list(papers_for_direction))
        lines.append("")

    lines.extend(["## 6. 每个方向的研究空白", ""])
    for direction in direction_order():
        item = metrics[direction]
        lines.append(f"### {direction} - {item['direction_zh']}")
        lines.append(f"- 研究空白判断：{item['main_risk_cn']}")
        for gap in GAP_HINTS[direction]:
            lines.append(f"- {gap}")
        if direction in NOISE_NOTES:
            lines.append(f"- 数据不足，需人工补充检索：{NOISE_NOTES[direction]}")
        lines.append("")

    lines.extend(["## 7. 每个方向的实验可行性", ""])
    for direction in direction_order():
        item = metrics[direction]
        lines.append(
            f"- {direction} - {item['direction_zh']}：实验难度 {difficulty_label(item['experimental_feasibility'])}；"
            f"设备需求 {equipment_label(item['equipment_accessibility'])}；发表潜力 {score_label(item['publication_potential'])}。主要风险：{item['main_risk_cn']}"
        )
    lines.append("")

    lines.extend(["## 8. 每个方向可能的论文题目", ""])
    lines.append("以下为基于数据线索形成的可拟题目，不是已发表论文题录。")
    lines.append("")
    for direction in direction_order():
        item = metrics[direction]
        lines.append(f"### {direction} - {item['direction_zh']}")
        for title in TITLE_HINTS[direction]:
            lines.append(f"- 可拟题目：{title}")
        lines.append("")

    lines.extend(["## 9. 推荐主攻方向", ""])
    lines.extend(recommendation_lines(scores, "主攻方向"))
    lines.append("")
    lines.append("主攻逻辑：E 能把固废资源化、碳化活化和水泥基性能直接连接；D 实验设备门槛较低、混凝土相关性强，但必须与材料体系或过程强化耦合以避免重复性选题。")
    lines.append("")

    lines.extend(["## 10. 推荐备用方向", ""])
    lines.extend(recommendation_lines(scores, "备用方向"))
    lines.append("")
    lines.append("备用逻辑：A 与“超重力”主题最贴近，但设备可获得性和固废成分波动是主要风险。建议先把 A 作为 E/D 的强化碳化工艺变量，而不是立即独立成大课题。")
    lines.append("")

    lines.extend(
        [
            "## 11. 第一轮最小可行实验方案",
            "",
            "- 目标：用普通材料实验室可执行的小试验证“预碳化固废 SCM + CO2 养护”是否能同时改善早期性能和固碳表现。",
            "- 材料：优先选择一种来源稳定的废混凝土粉或钢渣粉；设置未碳化、常规静态碳化、强化碳化三个材料状态。若无超重力设备，强化碳化先用高 CO2 浓度、湿度和搅拌/薄层暴露模拟。",
            "- 基准体系：水泥净浆或砂浆，设置 0%、10%、20% 固废替代率；D/E 主线先做砂浆强度、质量变化、pH/酚酞、XRD/TG 或碳酸盐含量等基础指标。",
            "- 判据：若 10%-20% 替代率下强度不显著下降且碳酸盐生成/CO2 吸收有可测差异，则进入第二轮机制表征；若强度和工作性均恶化，则回到材料预处理和粒径分级。",
            "- 暂缓项：C/B/F 不纳入第一轮核心实验，只保留文献补检和设备条件评估。",
            "",
            "## 12. 下一步 30 天行动计划",
            "",
            "- 第 1 周：人工复核各方向代表论文，重点清理 B/C/F 的检索噪声；补检关键词中缺失的 cement paste、pipe pile、rotating packed bed mineral carbonation 交叉论文。",
            "- 第 2 周：确定 1-2 种固废来源、预碳化制度、基准水泥/砂浆配合比和最少测试指标；完成试验矩阵压缩。",
            "- 第 3 周：完成第一轮材料预碳化与砂浆/净浆小试，记录工作性、早期强度、质量变化和基础碳化表征。",
            "- 第 4 周：汇总实验数据与代表论文，判断主攻 E+D 或 E+D+A 耦合路线是否成立；若数据支撑不足，转入人工补充检索和第二轮方案修正。",
            "",
            "## 最终推荐表",
            "",
        ]
    )
    lines.extend(final_table(metrics))
    lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def generate_final_report(processed_dir: Path = DATA_PROCESSED, reports_dir: Path = REPORTS, output_path: Path | None = None) -> Path:
    data = load_inputs(processed_dir=processed_dir, reports_dir=reports_dir)
    output = output_path or reports_dir / "final_research_map.md"
    path = write_final_report(data, output)
    print(f"wrote {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the final hypergravity-concrete research map report.")
    parser.parse_args()
    generate_final_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
