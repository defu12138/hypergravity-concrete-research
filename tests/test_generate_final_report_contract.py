from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from generate_final_report import generate_final_report  # noqa: E402


def write_sample_inputs(processed: Path, reports: Path) -> None:
    processed.mkdir(parents=True)
    reports.mkdir(parents=True)
    directions = [
        ("A", "超重力碳化固废", "备用方向"),
        ("B", "离心/超重力成型混凝土", "暂缓方向"),
        ("C", "重力场对水泥水化影响", "暂缓方向"),
        ("D", "CO2养护与碳化混凝土", "主攻方向"),
        ("E", "碳化固废辅助胶凝材料", "主攻方向"),
        ("F", "旋转填充床与传质强化", "暂缓方向"),
    ]
    papers = []
    reading = []
    top_cited = []
    scores = []
    for index, (direction, zh, group) in enumerate(directions, start=1):
        papers.append(
            {
                "direction": direction,
                "direction_zh": zh,
                "title": f"{direction} concrete carbonation study",
                "year": 2024,
                "authors": "Author One; Author Two",
                "venue": "Journal of Cement Data",
                "doi": f"10.1234/{direction.lower()}",
                "url": "https://example.org/paper",
                "abstract": "cement concrete carbonation high gravity",
                "citation_count": 10 * index,
                "source_database": "OpenAlex",
            }
        )
        reading.append(
            {
                "direction": direction,
                "title": f"{direction} recommended paper",
                "year": 2023,
                "authors": "Reading Author",
                "venue": "Recommended Journal",
                "doi": f"10.5678/{direction.lower()}",
                "url": "https://example.org/reading",
                "citation_count": 100 - index,
                "abstract": "relevant abstract",
                "relevance_reason_cn": "相关：命中主题关键词",
                "possible_inspiration_for_my_project_cn": "可作为材料体系或评价指标参考。",
            }
        )
        top_cited.append(
            {
                "direction": direction,
                "rank": 1,
                "title": f"{direction} top cited paper",
                "year": 2020,
                "authors": "Top Author",
                "venue": "Top Journal",
                "doi": f"10.9999/{direction.lower()}",
                "url": "https://example.org/top",
                "citation_count": 500 - index,
                "source_database": "OpenAlex",
                "query": "concrete carbonation",
            }
        )
        scores.append(
            {
                "direction": direction,
                "direction_zh": zh,
                "overall_score": 4.5 - index * 0.2,
                "literature_heat": 5 - index * 0.3,
                "maturity": 3.5,
                "novelty_space": 4.0,
                "experimental_feasibility": 4.0 if direction in {"D", "E"} else 2.5,
                "equipment_accessibility": 4.0 if direction in {"D", "E"} else 2.0,
                "concrete_relevance": 5.0,
                "publication_potential": 4.0,
                "recommendation_group": group,
                "main_risk_cn": "主要风险来自设备或材料波动。",
                "score_explanation_cn": "基于样例评分。",
                "data_evidence_cn": "论文总数=1；2022-2026近五年=1；增长=1。",
            }
        )
    pd.DataFrame(papers).to_csv(processed / "papers_master.csv", index=False)
    pd.DataFrame(reading).to_csv(processed / "reading_list_by_direction.csv", index=False)
    pd.DataFrame(top_cited).to_csv(processed / "top_cited_papers.csv", index=False)
    pd.DataFrame(scores).to_csv(processed / "direction_score.csv", index=False)
    (reports / "landscape_summary.md").write_text("# 文献景观总结\n\n## A - 超重力碳化固废\n\n样例现状。", encoding="utf-8")
    (reports / "reading_list_by_direction.md").write_text("# 分方向推荐阅读清单\n\n样例阅读清单。", encoding="utf-8")
    (reports / "direction_score_report.md").write_text("# 方向可行性评分报告\n\n样例评分。", encoding="utf-8")


def test_generate_final_report_writes_required_sections_and_table(tmp_path: Path) -> None:
    processed = tmp_path / "data" / "processed"
    reports = tmp_path / "reports"
    write_sample_inputs(processed, reports)

    output = generate_final_report(processed_dir=processed, reports_dir=reports)

    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "# 超重力与混凝土结合方向的文献侦察与选题可行性分析" in text
    for section in [
        "## 1. 研究背景",
        "## 2. 调研方法",
        "## 3. 六个方向总体对比",
        "## 4. 每个方向的研究现状",
        "## 5. 每个方向的代表论文",
        "## 6. 每个方向的研究空白",
        "## 7. 每个方向的实验可行性",
        "## 8. 每个方向可能的论文题目",
        "## 9. 推荐主攻方向",
        "## 10. 推荐备用方向",
        "## 11. 第一轮最小可行实验方案",
        "## 12. 下一步 30 天行动计划",
    ]:
        assert section in text
    assert "| 方向 | 热度 | 创新性 | 实验难度 | 设备需求 | 推荐程度 |" in text
    assert "A recommended paper" in text
    assert "可拟题目" in text
    assert "TBD" not in text
    assert "TODO" not in text


def test_generate_final_report_marks_missing_inputs_as_data_gap(tmp_path: Path) -> None:
    processed = tmp_path / "data" / "processed"
    reports = tmp_path / "reports"
    processed.mkdir(parents=True)
    reports.mkdir(parents=True)

    output = generate_final_report(processed_dir=processed, reports_dir=reports)

    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "数据不足，需人工补充检索" in text
    assert "| 方向 | 热度 | 创新性 | 实验难度 | 设备需求 | 推荐程度 |" in text
