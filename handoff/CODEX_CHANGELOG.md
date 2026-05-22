# CODEX_CHANGELOG

更新时间：2026-05-22

## 截至目前已完成的主要工作

- 建立并维护了“超重力与混凝土结合方向”的文献侦察项目结构。
- 围绕 A-F 六个方向完成初步文献检索与数据整理：
  - A - 超重力碳化固废
  - B - 离心/超重力成型混凝土
  - C - 重力场对水泥水化影响
  - D - CO2 养护与碳化混凝土
  - E - 碳化固废辅助胶凝材料
  - F - 旋转填充床与传质强化
- 对原始题录进行了 DOI、OpenAlex/Semantic Scholar ID、标题-年份相似度等维度的去重和清洗。
- 生成并整理了方向评分结果，形成 `reports/direction_score_report.md` 和相关 CSV 数据。
- 生成分方向阅读清单，形成 `reports/reading_list_by_direction.md` 与 `data/processed/reading_list_by_direction.csv`。
- 生成最终研究地图 `reports/final_research_map.md`，总结研究背景、方向对比、研究空白、代表论文、实验可行性、拟题方向和 30 天行动计划。
- 生成研究结果文件汇总 `reports/research_results_file_summary.xlsx`。
- 生成项目续接提示 `NEXT_SESSION_PROMPT.md`，明确后续不要从零开始、不要擅自扩展文献检索、优先围绕开题报告/精读/实验矩阵推进。

## 本次交接整理新增内容

- 新建 `handoff/` 目录，用于长期同步给 GPT/Codex 理解项目状态。
- 新增长期交接文件：
  - `handoff/PROJECT_STATE.md`
  - `handoff/CODEX_CHANGELOG.md`
  - `handoff/RESEARCH_DECISIONS.md`
  - `handoff/TODO_NEXT.md`
  - `handoff/NEXT_SESSION_PROMPT.md`
- 更新 `AGENTS.md`，加入交接文件维护、重要结论落盘、结束前执行 `git status`、提交前说明修改原因等规则。
- 更新 `.gitignore`，补充环境文件、密钥、虚拟环境、依赖目录和构建产物忽略规则。

## 重要约束

- 不要编造论文、作者、期刊、DOI 或实验结果。
- 不要删除已有研究成果文件。
- 不要重新设计方向评分体系，除非用户明确要求重新评估。
- 不要继续联网检索论文，除非用户明确要求。

## 2026-05-22 本地文献来源核验

- 任务：基于 `C:\Users\DELL\Desktop\超重力混凝土\孟老师资料\离心混凝土文献资料` 对当前项目自动检索结果做人工文献来源核验。
- 修改文件：
  - `data/local_literature/local_literature_index.csv`
  - `reports/local_literature/local_literature_audit.md`
  - `reports/local_literature/core_literature_candidates.md`
  - `.gitignore`
  - `handoff/PROJECT_STATE.md`
  - `handoff/CODEX_CHANGELOG.md`
  - `handoff/TODO_NEXT.md`
  - `handoff/NEXT_SESSION_PROMPT.md`
- 关键结论：本地 22 篇 PDF 中，主题明显偏 B（离心/超重力成型混凝土），可补强离心混凝土工程背景；对当前 E+D+A 主线仅局部补强，重点候选为 concrete sludge-derived material 相关文献和 CO2-CaO 干磨反应文献。
- 遗留问题：SCI 收录、JCR 分区、中科院分区、中文文献来源级别、部分 DOI/年份和是否最新综述/实验论文仍需人工核验。
- 原文控制：未复制或提交 PDF、Word、CAJ 或老师资料原件；`.gitignore` 已加入常见文献原文和压缩包扩展名。

## 2026-05-22 本地文献索引脚本

- 任务：新增 `scripts/index_local_literature.py`，用于扫描本地文献文件夹并生成 `data/local_literature/local_literature_index.csv`。
- 修改文件：
  - `scripts/index_local_literature.py`
  - `README.md`
  - `handoff/PROJECT_STATE.md`
  - `handoff/CODEX_CHANGELOG.md`
  - `handoff/RESEARCH_DECISIONS.md`
  - `handoff/TODO_NEXT.md`
  - `handoff/NEXT_SESSION_PROMPT.md`
- 关键结论：脚本仅索引文件属性、文件名线索和可选 PDF metadata，不做 OCR，不复制、不移动、不提交原始 PDF。
- 遗留问题：当前系统 `python` 命令可能是 Windows Store 占位符；脚本实际运行前需确认 Python 环境可用。

## 2026-05-22 本地文献主流 SCI 相关性核验

- 任务：基于本地文献索引和公开期刊页，对本地文献来源做主流 SCI/SCIE 相关性核验。
- 修改文件：
  - `data/local_literature/local_literature_sci_relevance.csv`
  - `reports/local_literature/sci_mainstream_relevance_audit.md`
  - `handoff/PROJECT_STATE.md`
  - `handoff/CODEX_CHANGELOG.md`
  - `handoff/RESEARCH_DECISIONS.md`
  - `handoff/TODO_NEXT.md`
  - `handoff/NEXT_SESSION_PROMPT.md`
- 关键结论：22 篇本地文献中，13 篇英文文献的来源期刊可通过公开期刊页确认 SCIE；但主线 E+D+A 的直接补强仍主要来自 concrete sludge-derived material 和 CO2-CaO dry grinding 两篇，B 方向文献数量和主流期刊背景最强。
- 遗留问题：中文文献、来源不明文献、JCR 分区和中科院分区仍需人工通过 Web of Science/JCR/中科院分区核验。
